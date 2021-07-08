#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Learner API Verification tasks module """
import simplejson
from celery import group
from celery.exceptions import Reject
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Max
from django.db.models import Min

from tesla_ce import celery_app
from tesla_ce import models
from ..reports import update_learner_activity_instrument_report


@celery_app.task(ignore_result=True)
def create_request(activity_id, learner_id, path, instruments, session_id=None):
    try:
        # Store the request
        learner = models.Learner.objects.get(learner_id=learner_id)

        # Check Informed Consent status
        if not learner.ic_status.startswith('VALID'):
            default_storage.delete(path)
            raise Reject("Missing informed consent", requeue=False)

        req = models.Request.objects.create(learner_id=learner.id,
                                            activity_id=activity_id,
                                            data=path,
                                            session_id=session_id)
        # Add the instruments
        req.instruments.set(instruments)
        if len(instruments) != req.instruments.count():
            error = {
                "message": 'Invalid instruments',
            }
            default_storage.save('{}.error'.format(path), ContentFile(simplejson.dumps(error).encode('utf-8')))
            req.status = 2
            req.error_message = error["message"]
            req.save()
            raise Reject("Invalid Instruments", requeue=False)

        # Analyse this request
        verify_request.apply_async((req.id, ))
        default_storage.save('{}.valid'.format(path), ContentFile(simplejson.dumps({
            "message": "stored",
            "request_id": req.id
        }).encode('utf-8')))
        return req.id
    except models.Learner.DoesNotExist:
        raise Reject("Invalid Learner", requeue=False)


@celery_app.task(ignore_result=True)
def verify_request(request_id, result_id=None):
    """
        Start verification of a request

        :param request_id: Sample ID
        :type request_id: int
        :param result_id: Verification Request ID. Used by provider workers
        :type result_id: int
    """
    try:
        # Get the request
        request = models.Request.objects.get(id=request_id)

        # Create verification results for active providers
        request_task_group = []
        for instrument in request.instruments.all():
            instrument_task_group = []

            # Create the result for this instrument
            inst_result = models.RequestResult.objects.create(
                request_id=request_id,
                instrument_id=instrument.id
            )
            providers = models.Provider.objects.filter(instrument_id=instrument.id, enabled=True).all()
            if len(providers) == 0:
                inst_result.status = 4
                inst_result.save()
            else:
                for provider in providers:
                    req_result = models.RequestProviderResult.objects.create(
                        request=request,
                        provider=provider
                    )

                    try:
                        enrolment = models.Enrolment.objects.get(learner_id=request.learner_id, provider_id=provider.id)
                    except models.Enrolment.DoesNotExist:
                        enrolment = None

                    # check if instrument needs enrolment
                    if instrument.requires_enrolment is True and (enrolment is None or not enrolment.can_analyse):
                        req_result.status = 5
                        req_result.save()
                    else:
                        instrument_task_group.append(verify_request.s(request_id,
                                                                      req_result.id).set(queue=provider.queue))
                if len(instrument_task_group) == 0:
                    inst_result.status = 5
                    inst_result.save()
                else:
                    # Add instrument tasks to the request tasks
                    request_task_group += instrument_task_group

        if len(request_task_group) == 0:
            # There are no providers for any of the instruments
            if request.requestresult_set.filter(status=4).count() > 0:
                # Missing Provider
                request.status = 4
            elif request.requestresult_set.filter(status=5).count() > 0:
                # Missing Enrolment
                request.status = 5
            else:
                # Error
                request.status = 2
            request.save()
        else:
            # Launch processing tasks
            group(request_task_group).apply_async()

    except models.Request.DoesNotExist:
        raise Reject("Invalid Request", requeue=False)


@celery_app.task(ignore_result=True, bind=True)
def create_verification_summary(self, request_id, instrument_id):
    """
        Summarize request verification
        :param request_id: Request ID
        :type request_id: int
        :param request_id: Instrument ID
        :type request_id: int
    """
    try:
        result = models.RequestResult.objects.get(request_id=request_id, instrument_id=instrument_id)
    except models.RequestResult.DoesNotExist:
        result = models.RequestResult.objects.create(request_id=request_id, instrument_id=instrument_id,
                                                     code=0, status=0)

    res_values = models.RequestProviderResult.objects.filter(request_id=request_id,
                                                             provider__instrument_id=instrument_id,
                                                             status=1
                                                             ).aggregate(Max('result'), Max('code'))
    status_values = models.RequestProviderResult.objects.filter(request_id=request_id,
                                                                provider__instrument_id=instrument_id
                                                               ).aggregate(Min('status'), Max('status'))

    # Update status. If here are pending requests, set as PENDING, otherwise to the maximum status level
    result.status = 0
    if status_values['status__min'] > 0:
        result.status = status_values['status__max']
    # Compute average result for providers
    result.result = res_values['result__max']
    # Set the maximum alert level as the final level
    result.code = res_values['code__max']
    result.save()

    # If there are no missing requests for this learner and instrument in the activity, update the activity report
    if result.status > 0:
        # Check if all the instruments finished
        global_status_values = models.RequestProviderResult.objects.filter(
            request_id=request_id
        ).aggregate(Min('status'), Max('status'))

        # Update status. If there are pending requests, set as PENDING, otherwise to the maximum status level
        if global_status_values['status__min'] == 0:
            # There are pending results
            if global_status_values['status__max'] > 0:
                result.request.status = 2  # Processing
            else:
                result.request.status = 1  # Scheduled
        else:
            if global_status_values['status__max'] < 5:
                # Processed, Error, Timeout or Missing Provider
                result.request.status = global_status_values['status__max'] + 2
            else:
                result.request.status = 4  # Error
        result.request.save()

        # Update reports
        update_learner_activity_instrument_report.apply_async((result.request.learner_id,
                                                               result.request.activity_id,
                                                               instrument_id,))
