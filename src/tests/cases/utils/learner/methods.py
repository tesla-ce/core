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
""" TeSLA CE Learner actions for Use Case tests """
import mock
import requests

from django.utils import timezone

from tests import auth_utils
from tests.conftest import get_random_string

# List of submitted samples
samples_list = {}

# List of submitted requests
requests_list = {}


def api_learner_accept_ic(launcher):
    """
        The learner accepts the IC using the API
        :param launcher: Launcher object
    """
    # Authenticate with learner launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "LEARNER" in profile['roles']

    # Get required data
    institution_id = profile['institution']['id']

    # Get the current IC
    get_current_ic_resp = client.get('/api/v2/institution/{}/ic/current/'.format(institution_id))
    assert get_current_ic_resp.status_code == 200

    # Accept the informed consent
    accept_ic_resp = client.post('/api/v2/institution/{}/learner/{}/ic/'.format(institution_id, profile['id']),
                                 data={'version': get_current_ic_resp.data['version']},
                                 format='json')
    assert accept_ic_resp.status_code == 200


def api_learner_enrolment(launcher):
    """
        A learner check their enrolment status via API.
        :param launcher: Launcher object
        :return: List of enrolments
    """
    # Authenticate with learner launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "LEARNER" in profile['roles']

    # Get the list of enrolments
    institution_id = profile['institution']['id']
    list_enrolments_resp = client.get(
        '/api/v2/institution/{}/learner/{}/enrolment/'.format(institution_id, profile['id'])
    )
    assert list_enrolments_resp.status_code == 200

    return list_enrolments_resp.data


def api_learner_missing_enrolment(launcher, activity, missing=False):
    """
        A learner check missing enrolments for an activity via API
        :param launcher: Launcher object
        :param activity: Activity object
        :param missing: True if missing enrolment is expected or False otherwise
        :return: List of enrolments
    """
    # Authenticate with learner launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "LEARNER" in profile['roles']

    # Get the list of enrolments
    institution_id = profile['institution']['id']
    list_enrolments_resp = client.get(
        '/api/v2/institution/{}/learner/{}/enrolment/?activity_id={}'.format(
            institution_id, profile['id'], activity['id']
        )
    )
    assert list_enrolments_resp.status_code == 200
    assert list_enrolments_resp.data['missing_enrolments'] == missing

    return list_enrolments_resp.data


def api_lapi_perform_enrolment(launcher, instruments):
    """
        The learner perform enrolment for missing instruments, sending data using LAPI and API
        :param launcher: Learner launcher object
        :param instruments: List of instruments to enrol
        :return: List of pending tasks assigned to providers
    """
    # List simulating the storage queue
    pending_tasks_storage = []
    # List simulating the validation queue
    pending_tasks_validation = []
    # Object simulating the providers validation queues
    pending_provider_tasks_validation = []

    def create_sample_test(*args, **kwargs):
        pending_tasks_storage.append(('create_sample', args, kwargs))

    def validate_request_test(*args, **kwargs):
        pending_tasks_validation.append(('validate_request', args, kwargs))

    def validate_request_prov_test(*args, **kwargs):
        pending_provider_tasks_validation.append(('validate_request', args, kwargs))

    # Authenticate with learner launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "LEARNER" in profile['roles']

    # Get learner data (it is injected with the JS script)
    inst_id = profile['institution']['id']
    learner_data_resp = client.get('/api/v2/institution/{}/learner/{}/'.format(inst_id, profile['id']))
    assert learner_data_resp.status_code == 200
    learn_id = learner_data_resp.data['learner_id']

    # Create a data object simulating a sensor capture
    sensor_data = {
        'learner_id': learn_id,
        'instruments': [],
        'metadata': {
            'mimetype': 'some/mimetype',
            'filename': None,
            'created_at': None,
            'context': {}
        },
        'data': None
    }
    with mock.patch('tesla_ce.tasks.requests.enrolment.create_sample.apply_async', create_sample_test):
        for inst in instruments:
            sensor_data['instruments'] = [inst]
            # Send samples
            for _ in range(4*inst):
                sensor_data['data'] = get_random_string(50)
                sensor_data['created_at']: timezone.now()
                data_sent_resp = client.post(
                    '/lapi/v1/enrolment/{}/{}/'.format(inst_id, learn_id),
                    data=sensor_data,
                    format='json'
                )
                assert data_sent_resp.status_code == 200
                assert data_sent_resp.data['status'] == 'OK'
                if learn_id not in samples_list:
                    samples_list[learn_id] = []
                samples_list[learn_id].append(data_sent_resp.data['path'])

    # Run storage tasks
    with mock.patch('tesla_ce.tasks.requests.enrolment.validate_request.apply_async', validate_request_test):
        from tesla_ce.tasks.requests.enrolment import create_sample
        for task in pending_tasks_storage:
            assert task[0] == 'create_sample'
            create_sample(**task[2]['kwargs'])

    # Run validation tasks
    with mock.patch('tesla_ce.tasks.requests.enrolment.validate_request.apply_async', validate_request_prov_test):
        from tesla_ce.tasks.requests.enrolment import validate_request
        for task in pending_tasks_validation:
            assert task[0] == 'validate_request'
            validate_request(*task[1][0])

    # Return pending provider validation tasks
    return pending_provider_tasks_validation


def lapi_check_requests_status(launcher, expected_status):
    """
        The learner check the status of sent requests using LAPI
        :param launcher: Learner launcher object
        :param expected_status: The expected status for requests
    """
    lapi_check_sample_status(launcher, expected_status, requests_list)


def lapi_check_sample_status(launcher, expected_status, input_list=None):
    """
        The learner check the status of sent samples using LAPI
        :param launcher: Learner launcher object
        :param expected_status: The expected status for samples
        :param input_list: List of samples to check
    """
    if isinstance(expected_status, str):
        expected_status = [expected_status]

    if input_list is None:
        input_list = samples_list

    # Authenticate with learner launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "LEARNER" in profile['roles']

    # Get learner data (it is injected with the JS script)
    inst_id = profile['institution']['id']
    learner_data_resp = client.get('/api/v2/institution/{}/learner/{}/'.format(inst_id, profile['id']))
    assert learner_data_resp.status_code == 200
    learn_id = learner_data_resp.data['learner_id']

    # Check that this learner have sent data
    assert learn_id in input_list
    status_resp = client.post('/lapi/v1/status/{}/{}/'.format(inst_id, learn_id),
                              data={
                                  'samples': input_list[learn_id],
                                  'learner_id': learn_id,
                              }, format='json')
    assert status_resp.status_code == 200
    assert len(input_list[learn_id]) == len(status_resp.data)
    for stat in status_resp.data:
        assert stat['status'] in expected_status


def get_data_object_from_session(assessment_session):
    """
        Get data object from assessment session
        :param assessment_session: Assessment session object
        :return: Data object
    """
    # Get the data object
    injected_data_resp = requests.get(assessment_session['data']['data'], verify=False)
    assert injected_data_resp.status_code == 200
    data = injected_data_resp.json()

    # Authenticate with learner launcher credentials
    assert 'launcher' in data
    client = auth_utils.client_with_launcher_credentials(data['launcher'])

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "LEARNER" in profile['roles']

    assert data['learner']['id'] == profile['id']
    assert data['learner']['institution_id'] == profile['institution']['id']
    assert data['learner']['first_name'] == profile['first_name']
    assert data['learner']['last_name'] == profile['last_name']

    # Check that data contains the learner credentials
    assert 'token' in data
    assert 'access_token' in data['token']
    assert 'refresh_token' in data['token']

    # Check that data contains options
    assert 'options' in data
    assert 'floating_menu_initial_pos' in data['options']

    return injected_data_resp.json()


def lapi_learner_perform_activity(assessment_session):
    """
        The learner perform the activity, sending information from sensors using the LAPI
        :param assessment_session: Assessment session object
        :return: Tuple with the list of tasks pending to be executed by providers and performed activity
    """
    # Performed activity
    performed_activity = None

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

    # Get the assessment session data
    session_data = get_data_object_from_session(assessment_session)

    # Authenticate with learner launcher credentials
    client = auth_utils.client_with_token_credentials(session_data['token']['access_token'],
                                                      session_data['token']['refresh_token'])

    # Get the required data
    institution_id = session_data['learner']['institution_id']
    learner_id = session_data['learner']['learner_id']
    sensors = session_data['sensors']

    # Create a data object simulating a sensor capture
    sensor_data = {
        'learner_id': learner_id,
        'course_id': session_data['activity']['course']['id'],
        'activity_id': session_data['activity']['id'],
        'session_id': session_data['session_id'],
        'instruments': [],
        'metadata': {
            'mimetype': 'some/mimetype',
            'filename': None,
            'created_at': None,
            'context': {}
        },
        'data': None
    }
    with mock.patch('tesla_ce.tasks.requests.verification.create_request.apply_async', create_request_test):
        for sensor in sensors:
            if sensor == 'activity':
                # Activities are sent by VLE when learner submit them. Just create a random activity
                performed_activity = {
                    'filename': get_random_string(50),
                    'content': get_random_string(2048),
                    'mimetype': 'activity/mimetype'
                }
            else:
                sensor_data['instruments'] = sensors[sensor]
                sensor_data['metadata']['mimetype'] = '{}/mimetype'.format(sensor)
                # Send samples
                for capture_id in range(10):
                    sensor_data['data'] = get_random_string(50)
                    sensor_data['metadata']['created_at'] = timezone.now()
                    sensor_data['metadata']['context']['sequence'] = capture_id
                    data_sent_resp = client.post(
                        '/lapi/v1/verification/{}/{}/'.format(institution_id, learner_id),
                        data=sensor_data,
                        format='json'
                    )
                    assert data_sent_resp.status_code == 200
                    assert data_sent_resp.data['status'] == 'OK'
                    if learner_id not in requests_list:
                        requests_list[learner_id] = []
                    requests_list[learner_id].append(data_sent_resp.data['path'])

            # Learner can refresh the token
            new_token = auth_utils.refresh_token(session_data['token']['access_token'],
                                                 session_data['token']['refresh_token'])
            client = auth_utils.client_with_token_credentials(new_token['access_token'],
                                                              new_token['refresh_token'])

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

    return pending_provider_tasks_verification, performed_activity
