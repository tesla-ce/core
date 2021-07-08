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
""" TeSLA CE Use Case tests methods """
import io
import json
import random

import mock
import simplejson
import requests
import uuid

from django.utils import timezone

from tests import auth_utils
from tests.conftest import get_random_string
from tests.utils import get_provider_desc_file


def api_register_providers(global_admin):
    """
        A global administrator register the providers
        :param global_admin: Global admin object
        :return: Registered providers
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Get the list of instruments
    instruments = []
    stop = False
    while not stop:
        list_instruments_resp = client.get('/api/v2/admin/instrument/?offset={}'.format(len(instruments)))
        assert list_instruments_resp.status_code == 200
        instruments += list_instruments_resp.data['results']

        if len(instruments) == list_instruments_resp.data['count']:
            stop = True

    # Get the instruments we want to register
    fr_inst = None
    ks_inst = None
    plag_inst = None

    # Remove any existing provider
    for instrument in instruments:
        if instrument['acronym'] == 'fr':
            fr_inst = instrument['id']
        if instrument['acronym'] == 'ks':
            ks_inst = instrument['id']
        if instrument['acronym'] == 'plag':
            plag_inst = instrument['id']
        stop = False
        while not stop:
            list_inst_providers_resp = client.get('/api/v2/admin/instrument/{}/provider/'.format(instrument['id']))
            assert list_inst_providers_resp.status_code == 200
            if list_inst_providers_resp.data['count'] > 0:
                for inst_prov in list_inst_providers_resp.data['results']:
                    del_providers_resp = client.delete(
                        '/api/v2/admin/instrument/{}/provider/{}/'.format(instrument['id'], inst_prov['id'])
                    )
                    assert del_providers_resp.status_code == 204
            else:
                stop = True

    providers = {}

    # Register a FR provider
    fr_desc = json.load(open(get_provider_desc_file('fr_tfr'), 'r'))
    fr_desc['enabled'] = True
    fr_desc['validation_active'] = True
    if 'instrument' in fr_desc:
        del fr_desc['instrument']
    fr_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(fr_inst),
                                        data=fr_desc,
                                        format='json')
    assert fr_prov_register_resp.status_code == 201
    providers['fr'] = fr_prov_register_resp.data
    providers['fr']['deferred'] = False

    # Register a KS provider
    ks_desc = json.load(open(get_provider_desc_file('ks_tks'), 'r'))
    ks_desc['enabled'] = True
    ks_desc['validation_active'] = True
    if 'instrument' in ks_desc:
        del ks_desc['instrument']
    ks_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(ks_inst),
                                        data=ks_desc,
                                        format='json')
    assert ks_prov_register_resp.status_code == 201
    providers['ks'] = ks_prov_register_resp.data
    providers['ks']['deferred'] = False

    # Register a Plagiarism provider
    pt_desc = json.load(open(get_provider_desc_file('pt_tpt'), 'r'))
    pt_desc['enabled'] = True
    if 'instrument' in pt_desc:
        del pt_desc['instrument']
    pt_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(plag_inst),
                                        data=pt_desc,
                                        format='json')
    assert pt_prov_register_resp.status_code == 201
    providers['plag'] = pt_prov_register_resp.data
    providers['plag']['deferred'] = False

    # Register a Plagiarism provider with deferred processing
    pt_desc2 = json.load(open(get_provider_desc_file('pt_turkund'), 'r'))
    pt_desc2['enabled'] = True  # TODO: Enable once deferred instruments are implemented on tests
    if 'instrument' in pt_desc2:
        del pt_desc2['instrument']
    pt2_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(plag_inst),
                                        data=pt_desc2,
                                        format='json')
    assert pt2_prov_register_resp.status_code == 201
    providers['plag_def'] = pt2_prov_register_resp.data
    providers['plag_def']['deferred'] = True

    # Enable the instruments
    fr_inst_enable_resp = client.patch('/api/v2/admin/instrument/{}/'.format(fr_inst),
                                       data={'enabled': True},
                                       format='json')
    assert fr_inst_enable_resp.status_code == 200
    ks_inst_enable_resp = client.patch('/api/v2/admin/instrument/{}/'.format(ks_inst),
                                       data={'enabled': True},
                                       format='json')
    assert ks_inst_enable_resp.status_code == 200
    pt_inst_enable_resp = client.patch('/api/v2/admin/instrument/{}/'.format(plag_inst),
                                       data={'enabled': True},
                                       format='json')
    assert pt_inst_enable_resp.status_code == 200

    return providers


def api_create_institution(global_admin, external_ic=False):
    """
        A global admin creates a new institution
        :param global_admin: Global admin object
        :param external_ic: True if the IC is managed externally, and assumed accepted, False otherwise
        :return: New created institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Create a new institution
    institution_data = {
        'name': "PyTest Test institution {}".format(get_random_string(5)),
        'acronym': get_random_string(10),
        'external_ic': external_ic
    }
    inst_create_resp = client.post('/api/v2/admin/institution/', data=institution_data, format='json')
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
    user_create_resp = client.post('/api/v2/admin/user/', data=user_data, format='json')
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
                                   data=user_data, format='json')
    assert user_create_resp.status_code == 201

    # Get institution legal admin object
    legal_admin_user = user_create_resp.data
    assert legal_admin_user['legal_admin']

    # Return credentials
    return {
        'email': email,
        'password': password
    }


def api_create_institution_send_admin(inst_admin):
    """
        An institution administrator creates a new SEND admin
        :param inst_admin: Institution admin object
        :return: New SEND administrator object
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
        'send_admin': True
    }
    user_create_resp = client.post('/api/v2/institution/{}/user/'.format(institution_id),
                                   data=user_data, format='json')
    assert user_create_resp.status_code == 201

    # Get institution SEND admin object
    send_admin_user = user_create_resp.data
    assert send_admin_user['send_admin']

    # Return credentials
    return {
        'email': email,
        'password': password
    }


def api_create_ic(admin):
    """
        A legal administrator of the institution creates the Informed Consent using the API
        :param admin: Credentials for a user with legal administration rights
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
                                 data=ic_data, format='json')
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
        data=ic_doc_data, format='json'
    )
    assert ic_doc_create_resp.status_code == 201
    new_ic_doc = ic_doc_create_resp.data

    assert new_ic_doc['consent']['id'] == version_id
    assert new_ic_doc['language'] == 'en'


def api_create_send_categories(admin, disabled_inst=[]):
    """
        A SEND administrator of the institution defines the SEND categories using the API
        :param admin: Credentials for a user with SEND administration rights
        :param disabled_inst: List of instruments to disable
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(admin['email'], admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Create an SEND category disabling KS
    institution_id = profile['institution']['id']
    send_cat_resp = client.post(
        '/api/v2/institution/{}/send/'.format(institution_id),
        data={
            'description': 'Test SEND category disabling KS',
            'data': {
                'enabled_options': [],
                'disabled_instruments': disabled_inst
            }
        },
        format='json'
    )
    assert send_cat_resp.status_code == 201
    send_category = send_cat_resp.data

    return send_category


def api_enable_direct_registration_vle(inst_admin):
    """
        Institution enables direct learners and instructors registration by VLE
        :param inst_admin: Institution admin credentials
        :return: VLE object
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(inst_admin['email'], inst_admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Enable direct registration
    institution_id = profile['institution']['id']
    inst_mod_resp = client.patch(
        '/api/v2/institution/{}/'.format(institution_id),
        data={
            'disable_vle_user_creation': False,
            'disable_vle_learner_creation': False,
            'disable_vle_instructor_creation': False,
        },
        format='json'
    )
    assert inst_mod_resp.status_code == 200
    assert not inst_mod_resp.data['disable_vle_user_creation']
    assert not inst_mod_resp.data['disable_vle_learner_creation']
    assert not inst_mod_resp.data['disable_vle_instructor_creation']


def api_register_vle(inst_admin):
    """
        Institution administrator register a new VLE
        :param inst_admin: Institution admin credentials
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
        data=vle_data, format='json'
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


def api_configure_activity(launcher, activity, providers):
    """
        An instructor configures the activity using the API
        :param launcher: Launcher object for an instructor
        :param activity: Activity object
        :param providers: List of enabled providers
    """
    # Authenticate with instructor launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "INSTRUCTOR" in profile['roles']

    # Get required data
    institution_id = profile['institution']['id']
    course_id = activity['course']['id']
    activity_id = activity['id']

    # Add KS as main instrument
    instrument_id = providers['ks']['instrument']['id']
    ks_data = {
        'active': True,
        'instrument_id': instrument_id
    }
    ks_add_response = client.post(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id),
        data=ks_data,
        format='json'
    )
    assert ks_add_response.status_code == 201
    # Add FR as an alternative instrument to KS
    instrument_id = providers['fr']['instrument']['id']
    fr_data = {
        'active': True,
        'options': {'online': True},
        'instrument_id': instrument_id,
        'alternative_to': ks_add_response.data['id']
    }
    fr_add_response = client.post(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id),
        data=fr_data,
        format='json'
    )
    assert fr_add_response.status_code == 201
    # Add plagiarism as main instrument
    instrument_id = providers['plag']['instrument']['id']
    plag_data = {
        'active': True,
        'instrument_id': instrument_id
    }
    plag_add_response = client.post(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id),
        data=plag_data,
        format='json'
    )
    assert plag_add_response.status_code == 201

    # Check that activity has now 3 instruments
    inst_list_response = client.get(
        '/api/v2/institution/{}/course/{}/activity/{}/instrument/'.format(institution_id, course_id, activity_id)
    )
    assert inst_list_response.status_code == 200
    assert inst_list_response.data['count'] == 3


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


def api_set_learner_send(admin, send_category, learner):
    """
        The SEND admin assigns send options to learner
        :param admin: Credentials for a user with SEND administration rights
        :param send_category: Send category object to be assigned to the learner
        :param learner: Learner object
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(admin['email'], admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Assign provided SEND category
    institution_id = profile['institution']['id']
    send_cat_resp = client.post(
        '/api/v2/institution/{}/learner/{}/send/'.format(institution_id, learner['id']),
        data={
            'category': send_category['id']
        },
        format='json'
    )
    assert send_cat_resp.status_code == 201


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


def get_task_by_queue(tasks):
    """
        Split a list of tasks on their respective queues
        :param tasks: List of tasks
        :return: Dictionary with tasks organized in queues
    """
    queues = {}
    for task in tasks:
        if task[2]['queue'] not in queues:
            queues[task[2]['queue']] = []
        queues[task[2]['queue']].append(task)
    return queues


def provider_validate_samples(providers, tasks):
    """
    Providers validate samples in their queues
    :param providers: Available providers
    :param tasks: Pending tasks to be processed
    :return: List of pending tasks
    """
    # List simulating the validation queue
    pending_tasks_validation = []

    def create_validation_summary(*args, **kwargs):
        pending_tasks_validation.append(('create_validation_summary', args, kwargs))

    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider is not None
        client, config = auth_utils.client_with_approle_credentials(provider['role_id'], provider['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        task_count = 0
        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'validate_request'
            learner_id, sample_id, validation_id = task[1][0]
            learner_id = str(learner_id)

            # Get Sample information
            get_sample_resp = client.get('/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/'.format(
                provider_id, learner_id, sample_id, validation_id)
            )
            assert get_sample_resp.status_code == 200
            sample = get_sample_resp.data

            # Download sample content
            sample_data_resp = requests.get(sample['sample']['data'], verify=False)
            assert sample_data_resp.status_code == 200
            sample['sample']['data'] = sample_data_resp.json()

            # Do validation
            val_result = {
                'status': (task_count % 2) + 1,  # Set half of the samples as not valid
                'error_message': None,
                'validation_info': {
                    'free_field1': 35,
                    'other_field':{
                        'status':3
                    }
                },
                'message_code_id': None,
                'contribution': 1.0 / (instrument_id * 2)  # We send four times samples than the instrument id
            }
            task_count +=1

            if deferred:
                # Deferred instrument
                samp_status_resp = client.post(
                    '/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/status/'.format(
                        provider_id, learner_id, sample_id, validation_id),
                                              data={"status": 7},  # WAITING_EXTERNAL_SERVICE
                                              format='json'
                                              )
                assert samp_status_resp.status_code == 200
                def_validation_result = {
                    'status': 7,  # WAITING_EXTERNAL_SERVICE
                    'error_message': None,
                    'validation_info': None,
                    'message_code_id': None,
                    'contribution': None
                }
                def_result = {
                    'result': def_validation_result,
                    'status': 7,
                    'info': {
                        'info_field1': 56,
                        'info_other_field': 'test',
                        'test_data_for_notification': {
                            'type': 'validation',
                            'url': '/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/'.format(
                                provider_id, learner_id, sample_id, validation_id
                            ),
                            'data': val_result
                        }
                    },
                    'learner_id': learner_id,
                    'sample_id': sample_id,
                    'validation_id': validation_id
                }
                # Set the result
                sample_deferred_validate_resp = client.put(def_result['info']['test_data_for_notification']['url'],
                                                           data=def_result['result'],
                                                           format='json')
                assert sample_deferred_validate_resp.status_code == 200

                # Send a notification request
                notification = {
                    'key': get_random_string(10),
                    'when': (timezone.now() + timezone.timedelta(seconds=-10)).isoformat(),  # Negative to ensure is due
                    'info': def_result['info']
                }
                send_notification_resp = client.post('/api/v2/provider/{}/notification/'.format(provider_id),
                                                     data=notification,
                                                     format='json')
                assert send_notification_resp.status_code == 201
            else:
                with mock.patch('tesla_ce.tasks.requests.enrolment.create_validation_summary.apply_async',
                                create_validation_summary):
                    send_validation_resp = client.put(
                        '/api/v2/provider/{}/enrolment/{}/sample/{}/validation/{}/'.format(
                            provider_id, learner_id, sample_id, validation_id),
                        data=val_result,
                        format='json'
                    )
                    assert send_validation_resp.status_code == 200

    return pending_tasks_validation


def worker_validation_summary(tasks):
    """
    Worker compute validation summary from individual validations
    :param tasks: Pending tasks to be processed
    :return: List of new pending tasks
    """
    # List simulating the enrolment queue
    pending_tasks_enrolment = []

    def enrol_learner_test(*args, **kwargs):
        pending_tasks_enrolment.append(('enrol_learner', args, kwargs))

    # Run validation summary tasks
    with mock.patch('tesla_ce.tasks.requests.enrolment.enrol_learner.apply_async', enrol_learner_test):
        from tesla_ce.tasks.requests.enrolment import create_validation_summary
        for task in tasks:
            assert task[0] == 'create_validation_summary'
            create_validation_summary(*task[1][0])

    return pending_tasks_enrolment


def worker_enrol_learner(tasks):
    """
        Worker distribute enrolment tasks among providers
        :param tasks: List of pending tasks
        :return: List of tasks assigned to each provider
    """
    # List simulating the enrolment queue
    pending_tasks_enrolment = []

    def enrol_learner_test(*args, **kwargs):
        pending_tasks_enrolment.append(('enrol_learner', args, kwargs))

    # Run validation summary tasks
    with mock.patch('tesla_ce.tasks.requests.enrolment.enrol_learner.apply_async', enrol_learner_test):
        from tesla_ce.tasks.requests.enrolment import enrol_learner
        for task in tasks:
            assert task[0] == 'enrol_learner'
            enrol_learner(*task[1][0])

    return pending_tasks_enrolment


def provider_enrol_learners(providers, tasks):
    """
    Provider perform learners enrolment
    :param providers: Available providers
    :param tasks: Pending tasks to be processed
    :return: List of new pending tasks
    """
    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider = None
        instrument_id = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider is not None
        assert instrument_id is not None
        client, config = auth_utils.client_with_approle_credentials(provider['role_id'], provider['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'enrol_learner'
            learner_id, sample_id = task[1][0]
            learner_id = str(learner_id)
            task_id = uuid.uuid4()

            # Get the model
            get_model_resp = client.post(
                '/api/v2/provider/{}/enrolment/'.format(provider_id),
                data={
                     'learner_id': learner_id,
                     'task_id': str(task_id)
                },
                format='json'
            )
            assert get_model_resp.status_code == 201
            model = get_model_resp.data
            model_data = None
            if model is not None and model['model'] is not None:
                model_data_resp = requests.get(model['model'], verify=False)
                assert model_data_resp.status_code == 200
                model_data = model_data_resp.json()

            # Get validated samples
            final = False
            val_samples = []
            while not final:
                val_samples_resp = client.get('/api/v2/provider/{}/enrolment/{}/available_samples/'.format(
                    provider_id, learner_id))
                assert val_samples_resp.status_code == 200
                val_samples += val_samples_resp.data['results']
                if val_samples_resp.data['count'] <= len(val_samples):
                    final = True

            # If there is no sample, unlock the model
            if len(val_samples) == 0:
                unlock_resp = client.post('/api/v2/provider/{}/enrolment/{}/unlock/'.format(provider_id, learner_id),
                                          data={
                                              'token': task_id
                                          },
                                          format='json')
                assert unlock_resp.status_code == 200
                continue

            # Get sample validations
            for sample in val_samples:
                # Get available validations
                final = False
                sample['validations'] = []
                while not final:
                    sample_vals_resp = client.get('/api/v2/provider/{}/enrolment/{}/sample/{}/validation/'.format(
                        provider_id, learner_id, sample_id))
                    assert sample_vals_resp.status_code == 200
                    sample['validations'] += sample_vals_resp.data['results']
                    if sample_vals_resp.data['count'] <= len(sample['validations']):
                        final = True
                # Get the sample data
                sample_data_resp = requests.get(sample['data'], verify=False)
                assert sample_data_resp.status_code == 200
                sample['data'] = sample_data_resp.json()

            # Perform the enrolment
            if model_data is None:
                model_data = {}
            new_model_data = model_data
            if 'num_samples' not in new_model_data:
                new_model_data['num_samples'] = 0
            if 'instrument_id' not in new_model_data:
                new_model_data['instrument_id'] = instrument_id
            new_model_data['num_samples'] += len(val_samples)
            new_percentage = 0
            if 'percentage' in new_model_data:
                new_percentage = new_model_data['percentage']
            sample_list = []
            if 'used_samples' in model:
                sample_list = model['used_samples']
            for sample in val_samples:
                sample_list.append(sample['id'])
                for validation in sample['validations']:
                    new_percentage += validation['contribution']
            new_model_data['percentage'] = min(1.0, new_percentage)
            model['valid'] = True
            model['model'] = new_model_data
            model['can_analyse'] = True
            model['percentage'] = new_model_data['percentage']
            model['used_samples'] = sample_list

            if deferred:
                pass
            else:
                # Save the model data
                model_data_save_resp = requests.post(model['model_upload_url']['url'],
                                                     data=model['model_upload_url']['fields'],
                                                     files={
                                                         'file': io.StringIO(simplejson.dumps(model['model']))
                                                     }, verify=False)
                assert model_data_save_resp.status_code == 204

                # Save the model and unlock it
                model_save_resp = client.put('/api/v2/provider/{}/enrolment/{}/'.format(provider_id, learner_id),
                                             data={
                                                 'learner_id': learner_id,
                                                 'task_id': task_id,
                                                 'percentage': model['percentage'],
                                                 'can_analyse': model['can_analyse'],
                                                 'used_samples': model['used_samples']
                                             },
                                             format='json')
                assert model_save_resp.status_code == 200


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


def lapi_lerner_perform_activity(assessment_session):
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
                continue
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


def vle_send_activity(vle, assessment_session, document):
    """
        The VLE send the submission performed by learner to TeSLA if required
        :param vle: VLE object
        :param assessment_session: Assessment session object
        :param document: Submitted document
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
    institution_id = session_data['learner']['institution_id']
    course_id = session_data['activity']['course']['id']
    activity_id = session_data['activity']['id']

    # Get the list of instruments waiting for document
    activity_instruments_resp = client.get('/api/v2/vle/{}/course/{}/activity/{}/attachment/{}/'.format(
        vle_id, course_id, activity_id, learner_id
    ))
    assert activity_instruments_resp.status_code == 200
    instruments = [inst['instrument'] for inst in activity_instruments_resp.data]

    # Make a submission of the document
    with mock.patch('tesla_ce.tasks.requests.verification.create_request.apply_async', create_request_test):
        data_sent_resp = client.post(
            '/lapi/v1/verification/{}/{}/'.format(institution_id, learner_id),
            data={
                'learner_id': learner_id,
                'course_id': session_data['activity']['course']['id'],
                'activity_id': session_data['activity']['id'],
                'session_id': session_data['session_id'],
                'instruments': instruments,
                'metadata': {
                    'mimetype': document['mimetype'],
                    'filename': document['filename'],
                    'created_at': timezone.now(),
                    'context': {}
                },
                'data': document['content']
            },
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


def provider_verify_request(providers, tasks):
    """
        Providers verify the information from requests in their queues
        :param providers: Available providers
        :param tasks: Pending tasks to be processed
        :return: List of pending tasks
    """
    # List simulating the verification queue
    pending_tasks_verification = []

    def create_verification_summary_test(*args, **kwargs):
        pending_tasks_verification.append(('create_verification_summary', args, kwargs))

    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider_creds = None
        instrument_id = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider_creds = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider_creds is not None
        assert instrument_id is not None
        client, config = auth_utils.client_with_approle_credentials(provider_creds['role_id'],
                                                                    provider_creds['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'verify_request'
            request_id, result_id = task[1][0]

            # Get the request
            get_request_resp = client.get('/api/v2/provider/{}/request/{}/'.format(provider_id, request_id))
            assert get_request_resp.status_code == 200
            request = get_request_resp.data
            learner_id = request['learner_id']

            # Get the provider data
            get_provider_resp = client.get('/api/v2/provider/{}/'.format(provider_id))
            assert get_provider_resp.status_code == 200
            provider = get_provider_resp.data

            # Get the model if necessary
            model_data = None
            if provider['instrument']['requires_enrolment']:
                # Download learner model
                get_model_resp = client.get('/api/v2/provider/{}/enrolment/{}/'.format(provider_id, learner_id))
                assert get_model_resp.status_code == 200
                model = get_model_resp.data
                assert model['can_analyse']

                # Get model data
                model_data_resp = requests.get(model['model'], verify=False)
                assert model_data_resp.status_code == 200
                model_data = model_data_resp.json()

            # Get request data
            request_data_resp = requests.get(request['request']['data'], verify=False)
            assert request_data_resp.status_code == 200
            request['request']['data'] = request_data_resp.json()

            # Instrument compute result without external services
            result_err = random.random() / 10.0  # Generate values with an error of maximum 10%
            if provider['inverted_polarity']:
                result = result_err
            else:
                result = 1.0 - result_err
            verification_result = {
                'status': 1,  # PROCESSED  (2 for ERROR)
                'error_message': None,
                'audit_data': {
                    'using_model': model_data is not None,
                    'some_other_field': get_random_string(15)
                },
                'result': result,
                'code': 1,  # OK  (2 WARNING, 3 ALERT)
                'message_code': None
            }

            # Perform verification
            if deferred:
                # Deferred instrument
                req_status_resp = client.post('/api/v2/provider/{}/request/{}/status/'.format(provider_id, request_id),
                                              data={"status": 7},  # WAITING_EXTERNAL_SERVICE
                                              format='json'
                                              )
                assert req_status_resp.status_code == 200
                def_verification_result = {
                    'status': 7,  # WAITING_EXTERNAL_SERVICE
                    'error_message': None,
                    'audit_data': {
                        'using_model': model_data is not None,
                        'some_other_field': get_random_string(15)
                    },
                    'result': None,
                    'code': 0,  # PENDING
                    'message_code': None
                }
                def_result = {
                    'result': def_verification_result,
                    'status': 7,
                    'info': {
                        'info_field1': 56,
                        'info_other_field': 'test',
                        'test_data_for_notification': {
                            'type': 'verification',
                            'url': '/api/v2/provider/{}/request/{}/'.format(provider_id, request_id),
                            'data': verification_result
                        }
                    },
                    'request_id': request_id,
                    'audit_data': {}
                }
                # Set the result
                req_deferred_verify_resp = client.put(def_result['info']['test_data_for_notification']['url'],
                                                      data=def_result['result'],
                                                      format='json')
                assert req_deferred_verify_resp.status_code == 200

                # Send a notification request
                notification = {
                    'key': get_random_string(10),
                    'when': (timezone.now() + timezone.timedelta(seconds=-10)).isoformat(),  # Negative to ensure is due
                    'info': def_result['info']
                }
                send_notification_resp = client.post('/api/v2/provider/{}/notification/'.format(provider_id),
                                                     data=notification,
                                                     format='json')
                assert send_notification_resp.status_code == 201
            else:
                with mock.patch('tesla_ce.tasks.requests.verification.create_verification_summary.apply_async',
                                create_verification_summary_test):
                    put_result_resp = client.put('/api/v2/provider/{}/request/{}/'.format(provider_id, request_id),
                                                 data=verification_result,
                                                 format='json'
                                             )
                    assert put_result_resp.status_code == 200

    return pending_tasks_verification


def worker_send_notifications():
    """
        Worker process notification tasks
        :return: List of pending provider notification tasks
    """
    # List simulating the notifications queue
    pending_tasks_notification = []

    def provider_notify_test(*args, **kwargs):
        pending_tasks_notification.append(('provider_notify', args, kwargs))

    # Process notifications
    with mock.patch('tesla_ce.tasks.notification.providers.provider_notify.apply_async',
                    provider_notify_test):
        from tesla_ce.tasks.notification.providers import send_provider_notifications
        send_provider_notifications()

    return pending_tasks_notification


def provider_process_notifications(providers, tasks, expected_type):
    """
        Providers process the notifications in their queues
        :param providers: Available providers
        :param tasks: Pending tasks to be processed
        :param expected_type: Type of expected notifications
        :return: List of pending tasks
    """
    # List simulating the proper queue depending on type of notification
    pending_tasks = []

    def create_validation_summary_test(*args, **kwargs):
        pending_tasks.append(('create_validation_summary', args, kwargs))

    def create_verification_summary_test(*args, **kwargs):
        pending_tasks.append(('create_verification_summary', args, kwargs))

    # Split tasks in queues
    queues = get_task_by_queue(tasks)

    # Each provider should process their tasks
    for queue_name in queues:
        provider_creds = None
        instrument_id = None
        deferred = False
        # Get the provider with this queue
        for prov in providers:
            if providers[prov]['queue'] == queue_name:
                instrument_id = providers[prov]['instrument']['id']
                provider_creds = providers[prov]['credentials']
                deferred = providers[prov]['deferred']
        assert provider_creds is not None
        assert instrument_id is not None
        assert deferred
        client, config = auth_utils.client_with_approle_credentials(provider_creds['role_id'],
                                                                    provider_creds['secret_id'])
        # Get the Provider ID from configuration
        provider_id = config['provider_id']

        for task in queues[queue_name]:
            # Get the parameters
            assert task[0] == 'provider_notify'
            notification_id = task[1][0][0]

            # Get notification content
            get_notification_resp = client.get('/api/v2/provider/{}/notification/{}/'.format(provider_id,
                                                                                             notification_id))
            assert get_notification_resp.status_code == 200
            notification = get_notification_resp.data

            # Get the information required to process the notification
            notification_type = notification['info']['test_data_for_notification']['type']
            url = notification['info']['test_data_for_notification']['url']
            data = notification['info']['test_data_for_notification']['data']
            assert notification_type == expected_type
            # Process each request depending on their type
            if notification_type == 'validation':
                with mock.patch('tesla_ce.tasks.requests.enrolment.create_validation_summary.apply_async',
                                create_validation_summary_test):
                    put_result_resp = client.put(url,
                                                 data=data,
                                                 format='json'
                                                 )
                    assert put_result_resp.status_code == 200
            elif notification_type == 'enrolment':
                model_url = notification['info']['test_data_for_notification']['model_url']
                model = notification['info']['test_data_for_notification']['model']
                # Save the model data
                model_data_save_resp = requests.post(model_url,
                                                     data=model['model_upload_url']['fields'],
                                                     files={
                                                         'file': io.StringIO(simplejson.dumps(model['model']))
                                                     }, verify=False)
                assert model_data_save_resp.status_code == 204

                # Save the model and unlock it
                model_save_resp = client.put(url,
                                             data=data,
                                             format='json')
                assert model_save_resp.status_code == 200
            elif notification_type == 'verification':
                with mock.patch('tesla_ce.tasks.requests.verification.create_verification_summary.apply_async',
                                create_verification_summary_test):
                    put_result_resp = client.put(url,
                                                 data=data,
                                                 format='json'
                                                 )
                    assert put_result_resp.status_code == 200

    return pending_tasks


def worker_create_reports(tasks):
    """
        Worker process verification results to create the reports
        :param tasks: List of pending reporting tasks
    """
    # List simulating the reporting queue
    pending_tasks_reporting = []

    # List simulating the reporting queue
    pending_tasks_reporting2 = []

    def update_learner_activity_instrument_report_test(*args, **kwargs):
        pending_tasks_reporting.append(('update_learner_activity_instrument_report', args, kwargs))

    def update_learner_activity_report_test(*args, **kwargs):
        pending_tasks_reporting2.append(('update_learner_activity_report', args, kwargs))

    for task in tasks:
        assert task[0] == 'create_verification_summary'
        with mock.patch(
                'tesla_ce.tasks.reports.results.update_learner_activity_instrument_report.apply_async',
                update_learner_activity_instrument_report_test):
            from tesla_ce.tasks.requests.verification import create_verification_summary
            create_verification_summary(*task[1][0])

    # Perform reporting tasks
    for task in pending_tasks_reporting:
        assert task[0] == 'update_learner_activity_instrument_report'
        with mock.patch(
                'tesla_ce.tasks.reports.results.update_learner_activity_report.apply_async',
                update_learner_activity_report_test):
            from tesla_ce.tasks.reports.results import update_learner_activity_instrument_report
            update_learner_activity_instrument_report(*task[1][0])

    # Perform reporting tasks
    for task in pending_tasks_reporting2:
        assert task[0] == 'update_learner_activity_report'
        from tesla_ce.tasks.reports.results import update_learner_activity_report
        from celery.exceptions import Reject
        try:
            update_learner_activity_report(*task[1][0])
        except Reject:
            # Raised when no new data is available
            pass


def api_instructor_report(launcher, activity):
    """
        Instructor review the results for the activity
        :param launcher: Instructor launcher object
        :param activity: Activity object
    """
    # Authenticate with instructor launcher credentials
    client = auth_utils.client_with_launcher_credentials(launcher)

    # Get the user profile
    profile = auth_utils.get_profile(client)
    assert "INSTRUCTOR" in profile['roles']

    # Get required data
    institution_id = profile['institution']['id']
    course_id = activity['course']['id']
    activity_id = activity['id']

    # Get the list of reports from the activity
    activity_reports_resp = client.get('/api/v2/institution/{}/course/{}/activity/{}/report/'.format(
        institution_id,
        course_id,
        activity_id
    ))
    assert activity_reports_resp.status_code == 200
    reports = activity_reports_resp.data['results']

    # Get the detail for each report
    for report in reports:
        reports_detail_resp = client.get('/api/v2/institution/{}/course/{}/activity/{}/report/{}/'.format(
            institution_id,
            course_id,
            activity_id,
            report['id']
        ))
        assert reports_detail_resp.status_code == 200
        report['detailed_report'] = reports_detail_resp.data

    return reports
