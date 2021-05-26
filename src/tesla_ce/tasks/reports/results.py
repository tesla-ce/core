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
""" Assessment results report tasks module """
from celery.exceptions import Reject
from django.db.models import Avg
from django.db.models import Max
from django.db.models import Min

from tesla_ce import celery_app
from tesla_ce import models


@celery_app.task(ignore_result=True, bind=True)
def update_learner_activity_instrument_report(self, learner_id, activity_id, instrument_id):

    # Get the report
    try:
        report = models.ReportActivity.objects.get(
            activity_id=activity_id,
            learner_id=learner_id
        )
    except models.ReportActivity.DoesNotExist:
        report = models.ReportActivity.objects.create(
            activity_id=activity_id,
            learner_id=learner_id
        )
    # Get the instrument report detail
    try:
        instrument_report = models.ReportActivityInstrument.objects.get(
            report=report,
            instrument_id=instrument_id
        )
    except models.ReportActivityInstrument.DoesNotExist:
        try:
            instrument_report = models.ReportActivityInstrument.objects.create(
                report=report,
                instrument_id=instrument_id,
                enrolment=0,
                confidence=0,
                result=0
            )
        except Exception:
            # In the unprovable case two tasks try to access report the first time, one of them will fail on creation
            self.retry(countdown=(self.request.retries + 1) * 15, max_retries=5)
            return
    results_qs = models.RequestResult.objects.filter(request__activity_id=activity_id,
                                                     instrument_id=instrument_id,
                                                     request__learner_id=learner_id)

    # Compute the final alert levels from result codes
    code_result = results_qs.filter(status=1).aggregate(Max('code'), Avg('result'))
    instrument_report.result = round(code_result['result__avg'] * 100)
    instrument_report.confidence = round(results_qs.filter(status=1).count() / results_qs.count() * 100)
    code = code_result['code__max']
    if code > 0:
        # Unless the code is 0 (PENDING), move to the alerts scale
        code += 1
    # Update levels where this instrument applies
    if instrument_report.instrument.identity:
        instrument_report.identity_level = code
    else:
        instrument_report.identity_level = 1 # No data
    if instrument_report.instrument.originality or instrument_report.instrument.authorship:
        instrument_report.content_level = code
    else:
        instrument_report.authorship_level = 1 # No data
    if instrument_report.instrument.integrity:
        instrument_report.integrity_level = code
    else:
        instrument_report.integrity_level = 1 # No data
    # Get mean enrolment value from used providers
    instrument_report.enrolment = round(models.Enrolment.objects.filter(
        learner_id=learner_id,
        provider_id__in=results_qs.values_list(
            'request__requestproviderresult__provider_id',
            flat=True).distinct()
    ).aggregate(Min('percentage'))['percentage__min'] * 100)
    instrument_report.save()

    # Update the report
    update_learner_activity_report.apply_async((learner_id, activity_id,))


@celery_app.task(ignore_result=True)
def update_learner_activity_report(learner_id, activity_id):
    # Skip update if no new data is present
    try:
        report = models.ReportActivity.objects.get(
            activity_id=activity_id,
            learner_id=learner_id
        )
    except models.ReportActivity.DoesNotExist:
        # This task is executed always after instrument results tasks. It is not possible that report does not exist
        raise Reject('Report does not exists')
    if report.updated_at > report.reportactivityinstrument_set.aggregate(Max('updated_at'))['updated_at__max']:
        raise Reject('No new results')

    stats = report.reportactivityinstrument_set.aggregate(Max('identity_level'),
                                                          Max('content_level'),
                                                          Max('integrity_level'))
    # Update levels
    report.identity_level = stats['identity_level__max']
    report.content_level = stats['content_level__max']
    report.integrity_level = stats['integrity_level__max']

    report.save()


@celery_app.task(ignore_result=True)
def update_activity_report(activity_id):
    pass


@celery_app.task(ignore_result=True)
def update_course_report(course_id):
    pass
