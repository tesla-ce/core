#  Copyright (c) 2021 Xavier Baró
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
""" TeSLA CE VLE actions for Use Case tests """
import mock

from django.utils import timezone

from tests import auth_utils
from tests.conftest import get_random_string

from ..learner import get_data_object_from_session


def vle_create_course(vle):
    """
        The VLE creates a new course
        :param vle: Vle credentials
        :return: New created course
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Create a new course
    course_code = get_random_string(10)
    course_data = {
        'code': course_code,
        'description': "PyTest test course {}".format(course_code),
        'vle_course_id': get_random_string(5),
        'start': timezone.now() - timezone.timedelta(days=1),
        'end': timezone.now() + timezone.timedelta(weeks=4)
    }
    course_create_resp = client.post(
        '/api/v2/vle/{}/course/'.format(vle_id),
        data=course_data, format='json'
    )
    assert course_create_resp.status_code == 201
    course = course_create_resp.data

    return course


def vle_enrol_users(vle, course):
    """
        The VLE enrolls course learners and instructors
        :param vle: Vle credentials
        :param course: Course object
        :return: A tuple (instructors, learners) with enrolled instructors and learners
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Create learners
    learners = []
    for _ in range(2):
        username = get_random_string(10)
        email = '{}@tesla-ce.eu'.format(username)
        learner_data = {
            'username': username,
            'uid': username,
            'email': email,
            'first_name': username[:5],
            'last_name': username[5:]
        }
        learner_create_resp = client.post(
            '/api/v2/vle/{}/course/{}/learner/'.format(vle_id, course['id']),
            data=learner_data,
            format='json'
        )
        assert learner_create_resp.status_code == 201
        learners.append(learner_create_resp.data)

    # Create instructors
    instructors = []
    for _ in range(2):
        username = get_random_string(10)
        email = '{}@tesla-ce.eu'.format(username)
        learner_data = {
            'username': username,
            'uid': username,
            'email': email,
            'first_name': username[:5],
            'last_name': username[5:]
        }
        instructor_create_resp = client.post(
            '/api/v2/vle/{}/course/{}/instructor/'.format(vle_id, course['id']),
            data=learner_data,
            format='json'
        )
        assert instructor_create_resp.status_code == 201
        instructors.append(instructor_create_resp.data)

    return instructors, learners


def vle_create_activity(vle, course):
    """
        The VLE creates a new activity
        :param vle: Vle credentials
        :param course: Course object
        :return: New created activity
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Create an activity
    activity_create_resp = client.post(
        '/api/v2/vle/{}/course/{}/activity/'.format(vle_id, course['id']),
        data={
            'enabled': True,
            'code': get_random_string(10),
            'description': "PyTest test course",
            'vle_course_id': get_random_string(5),
            'vle_activity_type': 'quiz',
            'vle_activity_id': get_random_string(3)
        },
        format='json'
    )
    assert activity_create_resp.status_code == 201

    return activity_create_resp.data


def vle_check_learner_ic(vle, course, learner, missing=True):
    """
        VLE check the status of the Informed Consent of the learner
        :param vle: VLE credentials
        :param course: Course object
        :param learner: Learner object
        :param missing: True if it is expected that IC is not still accepted or False otherwise
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Create an activity
    learner_data_resp = client.get(
        '/api/v2/vle/{}/course/{}/learner/{}/'.format(vle_id, course['id'], learner['id']),
    )
    assert learner_data_resp.status_code == 200
    if missing:
        assert learner_data_resp.data['ic_status'].startswith('NOT_VALID')
    else:
        assert learner_data_resp.data['ic_status'].startswith('VALID')


def vle_create_assessment_session(vle, learner, activity, ic=True, enrolment=True, options=None):
    """
        The VLE creates an assessment session.
        :param vle: VLE object
        :param learner: Learner object
        :param activity: Activity object
        :param ic: True if IC is expected to be accepted or False otherwise
        :param enrolment: True if enrolment is expected to be performed or False otherwise
        :param options: Dictionary of options to customize the client
        :return: List of missing instruments
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Get an evaluation session
    create_session_resp = client.post(
        '/api/v2/vle/{}/assessment/'.format(vle_id),
        data={
            'vle_activity_type': activity['vle_activity_type'],
            'vle_activity_id': activity['vle_activity_id'],
            'vle_learner_uid': learner['uid'],
            'options': options
        },
        format='json'
    )
    if not ic:
        assert create_session_resp.status_code == 406
        assert create_session_resp.data['status'] == 2  # MISSING IC
        assert 'INFORMED CONSENT' in create_session_resp.data['message'].upper()
    elif not enrolment:
        assert create_session_resp.status_code == 406
        assert create_session_resp.data['status'] == 4  # MISSING ENROLMENT
        assert 'ENROLMENT' in create_session_resp.data['message'].upper()
    else:
        assert create_session_resp.status_code == 200

    # Check missing instruments
    return create_session_resp.data


def vle_create_launcher(vle, user, session=None):
    """
        The VLE creates a launcher for the user
        :param vle: VLE object
        :param user: User object
        :param session: Assessment session object
        :return: New launcher data
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Get data for launcher
    data = {
        'vle_user_uid': user['uid']
    }

    if session is not None:
        data['session_id'] = session['id']

    # Create a launcher
    launcher_create_resp = client.post('/api/v2/vle/{}/launcher/'.format(vle_id), data=data)
    assert launcher_create_resp.status_code == 200

    launcher = launcher_create_resp.data
    return launcher


def vle_send_activity(vle, assessment_session, document, omit_session=False):
    """
        The VLE send the submission performed by learner to TeSLA if required
        :param vle: VLE object
        :param assessment_session: Assessment session object
        :param document: Submitted document
        :param omit_session: If True, activity is sent without session
        :return: Pending tasks
    """
    # List simulating the storage queue
    pending_tasks_storage = []
    # List simulating the verification queue
    pending_tasks_verification = []
    # Object simulating the providers verification queues
    pending_provider_tasks_verification = []

    def create_request_test(*args, **kwargs):
        pending_tasks_storage.append(('create_request', args, kwargs))

    def verify_request_test(*args, **kwargs):
        pending_tasks_verification.append(('verify_request', args, kwargs))

    def verify_request_prov_test(*args, **kwargs):
        pending_provider_tasks_verification.append(('verify_request', args, kwargs))

    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the options for verification
    session_data = get_data_object_from_session(assessment_session)

    # If no document is required just return an empty list of tasks
    if document is None:
        assert 'activity' not in session_data['sensors']
        return []

    # Get required data
    vle_id = config['vle_id']
    learner_id = session_data['learner']['learner_id']
    course_id = session_data['activity']['course']['id']
    activity_id = session_data['activity']['id']

    # Get the list of instruments waiting for document
    activity_instruments_resp = client.get('/api/v2/vle/{}/course/{}/activity/{}/attachment/{}/'.format(
        vle_id, course_id, activity_id, learner_id
    ))
    assert activity_instruments_resp.status_code == 200
    instruments = [inst['instrument'] for inst in activity_instruments_resp.data]

    # Create the document data
    document_data = {
                'session_id': session_data['session_id'],
                'instruments': instruments,
                'metadata': {
                    'mimetype': document['mimetype'],
                    'filename': document['filename'],
                    'created_at': timezone.now(),
                    'context': {}
                },
                'data': document['content']
            }
    if omit_session:
        del document_data['session_id']

    # Make a submission of the document
    with mock.patch('tesla_ce.tasks.requests.verification.create_request.apply_async', create_request_test):
        data_sent_resp = client.post(
            '/api/v2/vle/{}/course/{}/activity/{}/attachment/{}/'.format(
                vle_id, course_id, activity_id, learner_id
            ),
            data=document_data,
            format='json'
        )
        assert data_sent_resp.status_code == 200
        assert data_sent_resp.data['status'] == 'OK'

    # Run storage tasks
    with mock.patch('tesla_ce.tasks.requests.verification.verify_request.apply_async', verify_request_test):
        from tesla_ce.tasks.requests.verification import create_request
        for task in pending_tasks_storage:
            assert task[0] == 'create_request'
            create_request(**task[2]['kwargs'])

    # Run verification tasks
    with mock.patch('tesla_ce.tasks.requests.verification.verify_request.apply_async', verify_request_prov_test):
        from tesla_ce.tasks.requests.verification import verify_request
        for task in pending_tasks_verification:
            assert task[0] == 'verify_request'
            verify_request(task[1][0][0])

    return pending_provider_tasks_verification


def vle_activity_report(vle, activity):
    """
        VLE request the results for the activity
        :param vle: VLE object
        :param activity: Activity object
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get required data
    vle_id = config['vle_id']

    # Get required data
    course_id = activity['course']['id']
    activity_id = activity['id']

    # Get the list of reports from the activity
    activity_reports_resp = client.get('/api/v2/vle/{}/course/{}/activity/{}/report/'.format(
        vle_id,
        course_id,
        activity_id
    ))
    assert activity_reports_resp.status_code == 200
    reports = activity_reports_resp.data['results']

    # Get the detail for each report
    for report in reports:
        reports_detail_resp = client.get('/api/v2/vle/{}/course/{}/activity/{}/report/{}/'.format(
            vle_id,
            course_id,
            activity_id,
            report['id']
        ))
        assert reports_detail_resp.status_code == 200
        report['detailed_report'] = reports_detail_resp.data

        request_list = []
        final = False
        while not final:
            report_requests = client.get(
                '/api/v2/vle/{}/course/{}/activity/{}/learner/{}/request/?offset={}'.format(
                    vle_id,
                    course_id,
                    activity_id,
                    report['learner']['id'],
                    len(request_list)
            ))
            assert report_requests.status_code == 200
            request_list += report_requests.data['results']
            if len(request_list) >= report_requests.data['count']:
                final = True
        report['detailed_report']['requests'] = request_list

    return reports


def vle_close_assessment_session(vle, assessment_session):
    """
        The VLE creates an assessment session.
        :param vle: VLE object
        :param assessment_session: The assessment session to close
    """
    # Authenticate using VLE credentials
    client, config = auth_utils.client_with_approle_credentials(vle['role_id'], vle['secret_id'])

    # Get the VLE ID from configuration
    vle_id = config['vle_id']

    # Get an evaluation session
    close_session_resp = client.post(
        '/api/v2/vle/{}/assessment/'.format(vle_id),
        data={
            'session_id': assessment_session['id'],
            'close': True
        },
        format='json'
    )
    assert close_session_resp.status_code == 200
    assert close_session_resp.data['closed_at'] is not None

    # Check missing instruments
    return close_session_resp.data
