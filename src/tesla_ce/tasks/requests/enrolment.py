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
""" Learner API Enrolment tasks module """
import simplejson
from celery import group
from celery.exceptions import MaxRetriesExceededError
from celery.exceptions import Reject
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from tesla_ce import celery_app
from tesla_ce import models


@celery_app.task(ignore_result=True)
def create_sample(learner_id, path, instruments):
    try:
        # Store the sample
        learner = models.Learner.objects.get(learner_id=learner_id)

        # Check Informed Consent status
        if not learner.ic_status.startswith('VALID'):
            default_storage.delete(path)
            raise Reject("Missing informed consent", requeue=False)

        # Create the sample in the database
        sample = models.EnrolmentSample.objects.create(learner_id=learner.id,
                                                       data=path,
                                                       )
        # Add the instruments
        sample.instruments.set(instruments)
        if len(instruments) != sample.instruments.count():
            error = {
                "message": 'Invalid instruments',
            }
            default_storage.save('{}.error'.format(path), ContentFile(simplejson.dumps(error).encode('utf-8')))
            sample.status = 2
            sample.error_message = error["message"]
            sample.save()
            raise Reject("Invalid Instruments", requeue=False)

        # Once the sample has been stored, send validation task
        validate_request.apply_async((sample.learner.learner_id, sample.id, ))

        return sample.id
    except models.Learner.DoesNotExist:
        error = {
            "message": 'Invalid learner',
        }
        default_storage.save('{}.error'.format(path), ContentFile(simplejson.dumps(error).encode('utf-8')))
        raise Reject("Invalid Learner", requeue=False)


@celery_app.task(ignore_result=True)
def validate_request(learner_id, sample_id, validation_id=None):
    """
        Start validation of an enrolment sample
        :param learner_id: Learner identifier
        :type learner_id: str
        :param sample_id: Sample ID
        :type sample_id: int
        :param validation_id: Sample Validation ID. Used by provider workers
        :type validation_id: int
    """
    try:
        # Store the sample
        request = models.EnrolmentSample.objects.get(id=sample_id)

        # Get validators
        validators = []
        for instrument in request.instruments.all():
            inst_validators = instrument.provider_set.filter(enabled=True,
                                                             allow_validation=True,
                                                             validation_active=True).all()
            if len(inst_validators) == 0:
                validation = {
                    "status": "MISSING_PROVIDER",
                    "message": "There is no validation provider for instrument <{}>".format(instrument.name)
                }
                default_storage.save('{}.error'.format(request.data.name),
                                     ContentFile(simplejson.dumps(validation).encode('utf-8')))
                request.status = 2
                request.error_message = validation["message"]
                request.save()
                raise Reject("Missing Validation Providers", requeue=False)
            validators += list(inst_validators)

        # Perform the validation
        validation_group_tasks = []
        for validator in validators:
            valid_req = models.EnrolmentSampleValidation.objects.create(
                sample_id=sample_id,
                provider_id=validator.id
            )
            # TODO: Run validation task on each validator GROUP + RESULT TASK
            validation_group_tasks.append(validate_request.s(learner_id,
                                                             sample_id,
                                                             valid_req.id).set(queue=validator.queue))
        # Start tasks. Not using Chord to avoid requiring Providers to access the Database Backend
        group(validation_group_tasks).apply_async()
        #create_validation_summary.apply_async((learner_id, sample_id,), countdown=15)

    except models.EnrolmentSample.DoesNotExist:
        raise Reject("Invalid Sample", requeue=False)


@celery_app.task(bind=True, ignore_result=True, retry_backoff=True)
def create_validation_summary(self, learner_id, sample_id):
    """
        Summarize sample validation from the different validators
        :param learner_id: Learner identifier
        :type learner_id: str
        :param sample_id: Sample ID
        :type sample_id: int
    """

    # Get validations for this sample
    validations = models.EnrolmentSampleValidation.objects.filter(sample__learner__learner_id=learner_id,
                                                                  sample_id=sample_id)
    # TODO: Check if the current summary is newer than the last provider verification. (avoid updating finished summary)
    # Check if there are pending validations
    try:
        timeout = False
        if validations.filter(status=0).count() > 0:
            self.retry(countdown=15 + self.request.retries * 90, max_retries=5)
    except MaxRetriesExceededError:
        timeout = True

    # Get the sample
    sample = models.EnrolmentSample.objects.get(id=sample_id)

    # Intitialize validation data
    validation = {
        "status": None,
        "validations": {},
    }

    # Store the result
    valid = True
    for val_res in validations.all():
        if timeout and val_res.status == 0:
            val_res.status = 3
            val_res.save()
        if val_res.status > 1:
            valid = False
        info = None
        if val_res.info is not None and len(val_res.info.name) > 0:
            info = simplejson.loads(val_res.info.read().decode())
        validation['validations'][val_res.provider_id] = {
            'status': val_res.status,
            'status_code': val_res.get_status_display(),
            'error_message': val_res.error_message,
            'contribution': val_res.contribution,
            'info': info
        }

    if valid:
        validation['status'] = "VALID"
        sample.status = 1
        default_storage.save('{}.valid'.format(sample.data.name),
                             ContentFile(simplejson.dumps(validation).encode('utf-8')))
        # Start enrolment process
        enrol_learner.apply_async((learner_id, sample_id,))
    else:
        if timeout:
            validation['status'] = "TIMEOUT"
            sample.status = 3
            default_storage.save('{}.timeout'.format(sample.data.name),
                                 ContentFile(simplejson.dumps(validation).encode('utf-8')))
        else:
            validation['status'] = "ERROR"
            sample.status = 2
            default_storage.save('{}.error'.format(sample.data.name),
                                 ContentFile(simplejson.dumps(validation).encode('utf-8')))

    sample.save()


@celery_app.task(ignore_result=True)
def enrol_learner(learner_id, sample_id):
    """
        Perform learner enrolment for an instrument
        :param learner_id: Learner identifier
        :type learner_id: str
        :param sample_id: Sample ID
        :type sample_id: int
    """
    try:
        sample = models.EnrolmentSample.objects.get(id=sample_id)
        for instrument in sample.instruments.all():
            for provider in models.Provider.objects.filter(instrument_id=instrument.id, enabled=True).all():
                enrol_learner.apply_async((learner_id, sample_id,), queue=provider.queue)
    except models.EnrolmentSample.DoesNotExist:
        raise Reject(reason='Sample not found', requeue=False)
