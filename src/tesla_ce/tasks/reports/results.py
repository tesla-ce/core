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
import json
from celery.exceptions import Reject

from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
from django.db.models import Max
from django.db.models import Min
from django.db.models import Count

from tesla_ce import celery_app
from tesla_ce import models


@celery_app.task(ignore_result=True, bind=True)
def update_learner_activity_session_report(self, learner_id, activity_id, session_id, force_update=False):
    """
        Create a report for an assessment session
        :param self: Task object
        :param learner_id: Learner id
        :param activity_id: Activity id
        :param session_id: Assessment session id
        :param force_update: If True, compute data even if there are pending requests, otherwise is skipped
    """
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

    # Get the session report
    try:
        session_report = models.ReportActivitySession.objects.get(
            session_id=session_id
        )
    except models.ReportActivitySession.DoesNotExist:
        session_report = models.ReportActivitySession.objects.create(
            session_id=session_id,
            report=report,
            integrity_level=0,
            identity_level=0,
            content_level=0
        )

    # Get session requests statistics
    session_report.total_requests = models.Request.objects.filter(session_id=session_id).count()
    session_report.valid_requests = models.Request.objects.filter(session_id=session_id, status=3).count()
    session_report.pending_requests = models.Request.objects.filter(session_id=session_id, status__lt=3).count()
    session_report.processed_requests = models.Request.objects.filter(session_id=session_id, status__gte=3).count()

    # If all the data for this session is processed, compute session detail
    if session_report.pending_requests == 0 or force_update:
        results_qs = models.RequestResult.objects.filter(request__session_id=session_id,
                                                         request__learner_id=learner_id)
        data = {}
        results_stats = results_qs.filter(status=1).values('instrument').annotate(Max('code'),
                                                                                  Avg('result'),
                                                                                  Count('instrument'))
        for value in results_stats:
            if value['instrument'] not in data:
                data[value['instrument']] = {
                    'total': 0,
                    'valid': 0,
                    'confidence': None,
                    'result': None,
                    'code': None,
                }
            if value['code__max'] > 0:
                data[value['instrument']]['code'] = value['code__max'] + 1
            else:
                data[value['instrument']]['code'] = value['code__max']
            data[value['instrument']]['result'] = value['result__avg']
        num_requests = results_qs.values('instrument').annotate(Count('instrument'))
        for value in num_requests:
            if value['instrument'] not in data:
                data[value['instrument']] = {
                    'total': 0,
                    'valid': 0,
                    'confidence': None,
                    'result': None,
                    'code': None,
                }
            data[value['instrument']]['total'] = value['instrument__count']

        valid_requests = results_qs.filter(status=1).values('instrument').annotate(Count('instrument'))
        for value in valid_requests:
            if value['instrument'] not in data:
                data[value['instrument']] = {
                    'total': 0,
                    'valid': 0,
                    'confidence': None,
                    'result': None,
                    'code': None,
                }
            data[value['instrument']]['valid'] = value['instrument__count']
        for inst_id in data:
            if data[inst_id]['total'] > 0:
                data[inst_id]['confidence'] = data[inst_id]['valid'] / data[inst_id]['total']
            data[inst_id]['requests'] = json.dumps(
                list(results_qs.values_list('created_at', 'result').order_by('created_at')),
                cls=DjangoJSONEncoder)

        session_data = {
            'instruments': list(results_qs.values_list('instrument', flat=True).distinct()),
            'alerts': json.dumps(
                list(models.Alert.objects.filter(session_id=session_id).order_by('created_at')),
                cls=DjangoJSONEncoder),
            'data': data
        }
        data_path = '{}/results/{}/{}/{}/session_{}.json'.format(
                session_report.session.activity.vle.institution_id,
                session_report.session.learner.learner_id,
                session_report.session.activity.course.id,
                session_report.session.activity.id,
                session_id
            )
        session_report.data.save(data_path,
                                 ContentFile(json.dumps(session_data, cls=DjangoJSONEncoder).encode('utf-8')))

    session_report.save()


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
        instrument_report.identity_level = 1  # No data
    if instrument_report.instrument.originality or instrument_report.instrument.authorship:
        instrument_report.content_level = code
        instrument_report.authorship_level = code
    else:
        instrument_report.content_level = 1  # No data
        instrument_report.authorship_level = 1  # No data
    if instrument_report.instrument.integrity:
        instrument_report.integrity_level = code
    else:
        instrument_report.integrity_level = 1  # No data
    # Get mean enrolment value from used providers
    instrument_report.enrolment = 0
    if instrument_report.instrument.requires_enrolment:
        instrument_report.enrolment = round(models.Enrolment.objects.filter(
            learner_id=learner_id,
            provider_id__in=results_qs.values_list(
                'request__requestproviderresult__provider_id',
                flat=True).distinct()
        ).aggregate(Min('percentage'))['percentage__min'] * 100)
    instrument_report.save()

    # Update the audit data
    instrument_report.update_audit()

    # Update the report
    update_learner_activity_report.apply_async((learner_id, activity_id,))


@celery_app.task(ignore_result=True)
def update_learner_activity_report(learner_id, activity_id, force_update=False):
    """
        Update the report for an activity and learner
        :param learner_id: Learner id
        :param activity_id: Activity id
        :param force_update: If True, compute data even if there are pending requests, otherwise is skipped
    """
    # Skip update if no new data is present
    try:
        report = models.ReportActivity.objects.get(
            activity_id=activity_id,
            learner_id=learner_id
        )
    except models.ReportActivity.DoesNotExist:
        # This task is executed always after instrument results tasks. It is not possible that report does not exist
        raise Reject('Report does not exists')

    # If updated is forced, build instrument results
    if force_update:
        for inst_report in report.reportactivityinstrument_set.all():
            update_learner_activity_instrument_report(learner_id, activity_id, inst_report.instrument.id)

    # Check if there are new results
    last_update = report.reportactivityinstrument_set.aggregate(Max('updated_at'))['updated_at__max']
    if last_update is not None and report.updated_at > last_update and not force_update:
        raise Reject('No new results')

    stats = report.reportactivityinstrument_set.aggregate(Max('identity_level'),
                                                          Max('content_level'),
                                                          Max('integrity_level'))
    # Update levels
    report.identity_level = stats['identity_level__max']
    report.content_level = stats['content_level__max']
    report.integrity_level = stats['integrity_level__max']

    # Create the report data
    report_data = {
        'sessions': [],
        'documents': []
    }

    # Update sessions' results
    sessions = models.AssessmentSession.objects.filter(
        activity_id=activity_id,
        learner_id=learner_id
    ).values_list('id', flat=True)
    for session_id in list(sessions):
        update_learner_activity_session_report(learner_id=learner_id, activity_id=activity_id, session_id=session_id)

    for session in report.reportactivitysession_set.all().order_by('created_at'):
        closed_at = None
        if session.closed_at is not None:
            closed_at = session.closed_at.isoformat()
        session_data = None
        try:
            if session.data is not None:
                session_data = json.loads(session.data.read().decode())
        except Exception:
            # If there is any error reading the session data, just left it as None
            pass
        report_data['sessions'].append({
            'id': session.id,
            'pending_requests': session.pending_requests,
            'valid_requests': session.valid_requests,
            'processed_requests': session.processed_requests,
            'total_requests': session.total_requests,
            'created_at': session.created_at.isoformat(),
            'closed_at': closed_at,
            'identity_level': session.identity_level,
            'integrity_level': session.integrity_level,
            'content_level': session.content_level,
            'data': session_data
        })

    # Add results for attachments without session
    documents = models.Request.objects.filter(learner_id=learner_id,
                                              activity_id=activity_id,
                                              session__isnull=True).all()
    for doc in documents:
        doc_data = {}
        instruments = []
        for doc_res in doc.requestresult_set.values_list('instrument_id', 'status', 'result'):
            instruments.append(doc_res[0])
            doc_data[doc_res[0]] = {
                'status': doc_res[1],
                'result': doc_res[2]
            }
        report_data['documents'].append({
            'instruments': instruments,
            'results': doc_data,
            'created_at': doc.created_at.isoformat()
        })

    # Store report data
    data_path = '{}/results/{}/{}/{}/report.json'.format(
        report.activity.vle.institution_id,
        report.learner.learner_id,
        report.activity.course.id,
        report.activity.id
    )
    report.data.save(data_path,
                     ContentFile(json.dumps(report_data, cls=DjangoJSONEncoder).encode('utf-8')))
    report.save()


@celery_app.task(ignore_result=True)
def update_activity_report(activity_id):
    pass


@celery_app.task(ignore_result=True)
def update_course_report(course_id):
    pass
