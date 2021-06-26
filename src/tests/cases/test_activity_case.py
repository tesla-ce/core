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
""" TeSLA CE Activity use case test """
import pytest

from django.utils import timezone

from rest_framework.test import APIClient

from tests.conftest import get_random_string
from tests import auth_utils

def api_create_institution(global_admin):
    """
        A global admin creates a new institution
        :param global_admin: Global admin object
        :return: New created institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Create a new institution
    institution_data = {
        'name': "PyTest Test institution {}".format(get_random_string(5)),
        'acronym': get_random_string(10)
    }
    inst_create_resp = client.post('/api/v2/admin/institution/', data=institution_data, type='json')
    assert inst_create_resp.status_code == 201

    # Get institution object
    institution = inst_create_resp.data

    return institution


def api_create_institution_admin(global_admin, institution):
    """
        A global administrator creates a new user for the institution and assign administration rights
        :param global_admin: Global admin object
        :param institution: Institution object
        :return: New created institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Create a new user
    user_name = get_random_string(10)
    password = get_random_string(10)
    email = '{}@tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'institution_id': institution['id'],
        'login_allowed': True,
        'is_active': True,
        'is_staff': False,
        'password': password,
        'password2': password,
        'inst_admin': True
    }
    user_create_resp = client.post('/api/v2/admin/user/', data=user_data, type='json')
    assert user_create_resp.status_code == 201

    # Get institution admin object
    admin_user = user_create_resp.data
    assert 'ADMIN' in admin_user['roles']
    assert admin_user['institution']['id'] == institution['id']

    # Return credentials
    return {
        'email': email,
        'password': password
    }


def api_create_institution_legal_admin(inst_admin):
    """
        An institution administrator creates a new legal admin
        :param inst_admin: Institution admin object
        :return: New legal administrator object
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(inst_admin['email'], inst_admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Create a new user
    user_name = get_random_string(10)
    password = get_random_string(10)
    institution_id = profile['institution']['id']
    email = '{}@tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'institution': institution_id,
        'login_allowed': True,
        'password': password,
        'password2': password,
        'inst_admin': False,
        'legal_admin': True
    }
    user_create_resp = client.post('/api/v2/institution/{}/user/'.format(institution_id),
                                   data=user_data, type='json')
    assert user_create_resp.status_code == 201

    # Get institution legal admin object
    legal_admin_user = user_create_resp.data
    assert legal_admin_user['legal_admin']

    # Return credentials
    return {
        'email': email,
        'password': password
    }


def api_create_ic(admin):
    """
        A legal administrator of the institution creates the Informed Consent using the API
        :param admin: User with legal administration rights
        :param institution: Institution object
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(admin['email'], admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Create an IC
    institution_id = profile['institution']['id']
    ic_data = {
        'version': '1.0.0',
        'valid_from': timezone.now() - timezone.timedelta(days=1),
    }
    ic_create_resp = client.post('/api/v2/institution/{}/ic/'.format(institution_id),
                                 data=ic_data, type='json')
    assert ic_create_resp.status_code == 201
    new_ic = ic_create_resp.data
    assert new_ic['institution']['id'] == institution_id

    # Create a new IC document
    ic_doc_data = {
        'language': 'en',
        'html': '<h1>Informed Consent</h1>',
    }
    # TODO: Add PDF document
    version_id = new_ic['id']
    ic_doc_create_resp = client.post(
        '/api/v2/institution/{}/ic/{}/document/'.format(institution_id, version_id),
        data=ic_doc_data, type='json'
    )
    assert ic_doc_create_resp.status_code == 201
    new_ic_doc = ic_doc_create_resp.data

    assert new_ic_doc['consent']['id'] == version_id
    assert new_ic_doc['language'] == 'en'


def api_register_vle(inst_admin):
    """
    Institution administrator register a new VLE
    :param inst_admin: Institution admin object
    :return: VLE object
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(inst_admin['email'], inst_admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Register a VLE
    vle_name = get_random_string(10)
    vle_data = {
        'type': 0,  # 0 is the code for Moodle
        'name': vle_name,
        'url': '{}.tesla-ce-eu'.format(vle_name),
        'client_id': get_random_string(15)
    }
    institution_id = profile['institution']['id']
    vle_create_resp = client.post(
        '/api/v2/institution/{}/vle/'.format(institution_id),
        data=vle_data, type='json'
    )
    assert vle_create_resp.status_code == 201
    vle = vle_create_resp.data

    assert 'credentials' in vle
    assert 'role_id' in vle['credentials']
    assert 'secret_id' in vle['credentials']

    return vle['credentials']


def vle_create_course(vle):
    """
        The VLE creates a new course
        :param rest_api_client: API client
        :param vle: Vle object
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
        data=course_data, type='json'
    )
    assert course_create_resp.status_code == 201
    course = course_create_resp.data

    return course


def vle_enrol_users(rest_api_client, vle):
    """
        The VLE enrolls course learners and instructors
        :param rest_api_client: API client
        :param vle: Vle object
        :return: A tuple (instructors, learners) with enrolled instructors and learners
    """
    learners = []
    instructors = []

    return instructors, learners


def vle_create_activity(rest_api_client, vle, course):
    """
        The VLE creates a new activity
        :param rest_api_client: API client
        :param vle: Vle object
        :param course: Course object
        :return: New created activity
    """
    activity = None

    return activity


def api_configure_activity(rest_api_client, instructor, activity):
    """
        An instructor configures the activity using the API
        :param rest_api_client: API client
        :param instructor: Instructor object
        :param activity: Activity object
    """
    pass


def vle_check_learner_ic(rest_api_client, vle, learner, missing=True):
    """
        VLE check the status of the Informed Consent of the learner
        :param rest_api_client: API client
        :param vle: VLE object
        :param learner: Learner object
        :param missing: True if it is expected that IC is not still accepted or False otherwise
    """
    pass


def api_learner_accept_ic(rest_api_client, learner, launcher):
    """
        The leaerner accepts the IC using the API
        :param rest_api_client: API client
        :param learner: Learner object
        :param launcher: Launcher object
    """
    pass


def vle_check_learner_enrolment(rest_api_client, vle, learner, activity, missing=True):
    """
        The VLE checks the enrolment status of the learner.
        :param rest_api_client: API client
        :param vle: VLE object
        :param learner: Learner object
        :param activity: Activity object
        :param missing: True if missing enrolment is expected or False otherwise
        :return: List of missing instruments
    """
    instruments = []

    # Check missing instruments
    if missing:
        assert len(instruments) > 0
    else:
        assert len(instruments) == 0

    return instruments


def api_lapi_perform_enrolment(rest_api_client, learner, launcher, missing):
    """
        The learner perform enrolment for missing instruments, sending data using LAPI and API
        :param rest_api_client: API client
        :param learner: Learner object
        :param launcher: Launcher object
        :param missing: List of instruments with missing enrolment
    """
    pass


def vle_create_assessment_session(rest_api_client, vle, learner, activity):
    """
        The VLE creates an assessment session for a learner for the activity
        :param rest_api_client: API client
        :param vle: VLE object
        :param learner: Learner object
        :param activity: Activity object
        :return: New assessment session
    """
    assessment_session = None

    return assessment_session


def vle_create_launcher(rest_api_client, vle, learner, session=None):
    """
        The VLE creates a launcher for the learner
        :param rest_api_client: API client
        :param vle: VLE object
        :param learner: Learner object
        :param session: Assessment session object
        :return: New launcher data
    """
    launcher = None

    return launcher


def lapi_lerner_perform_activity(rest_api_client, learner, launcher, assessment_session):
    """
        The learner perform the activity, sending information from sensors using the LAPI
        :param rest_api_client: API client
        :param learner: Learner object
        :param launcher: Launcher object
        :param assessment_session: Assessment session object
    """
    pass


def api_instructor_report(rest_api_client, instructor, activity):
    """
        Instructor review the results for the activity
        :param rest_api_client: API client
        :param instructor: Instructor object
        :param activity: Activity object
    """
    pass


@pytest.mark.django_db(transaction=False)
def test_activity_case_complete(rest_api_client, user_global_admin):
    """
        Complete case use for TeSLA
        :param rest_api_client: API client
        :param user_global_admin: Global administrator object
    """

    # A global administrator creates a new institution
    institution = api_create_institution(user_global_admin)

    # A global administrator creates a new user for the institution and assign administration rights
    inst_admin = api_create_institution_admin(user_global_admin, institution)

    # Institution administrator creates a new legal admin
    legal_admin = api_create_institution_legal_admin(inst_admin)

    # A legal administrator of the institution creates the Informed Consent using the API
    api_create_ic(legal_admin)

    # Institution administrator register a new VLE
    vle = api_register_vle(inst_admin)

    # The VLE creates a new course
    course = vle_create_course(vle)

    # The VLE enrolls course learners and instructors
    instructors, learners = vle_enrol_users(rest_api_client, vle)

    pytest.skip('TODO')

    # The VLE creates a new activity
    activity = vle_create_activity(rest_api_client, vle, course)

    # An instructor configures the activity using the API
    api_configure_activity(rest_api_client, instructors[0], activity)

    # VLE check the status of the Informed Consent of the learner
    vle_check_learner_ic(rest_api_client, vle, learners[0], missing=True)

    # The VLE creates a launcher for the learner to accept IC
    launcher_ic = vle_create_launcher(rest_api_client, vle, learners[0])

    # The leaerner accepts the IC using the API
    api_learner_accept_ic(rest_api_client, learners[0], launcher_ic)

    # The VLE checks the enrolment status for the learner (missing is expected as is new learner)
    missing = vle_check_learner_enrolment(rest_api_client, vle, learners[0], activity, missing=True)

    # The VLE creates a launcher for the learner to perform the enrolment
    launcher_enrol = vle_create_launcher(rest_api_client, vle, learners[0])

    # The learner perform enrolment for missing instruments, sending data using LAPI
    api_lapi_perform_enrolment(rest_api_client, learners[0], launcher_enrol, missing)

    # The VLE creates an assessment session for a learner for the activity
    assessment_session = vle_create_assessment_session(rest_api_client, vle, learners[0], activity)

    # The VLE creates a launcher for the learner and assessment session
    launcher = vle_create_launcher(rest_api_client, vle, learners[0], assessment_session)

    # The learner perform the activity, sending information from sensors using the LAPI
    lapi_lerner_perform_activity(rest_api_client, learners[0], launcher, assessment_session)

    # Instructor review the results for the activity
    api_instructor_report(rest_api_client, instructors[0], activity)

