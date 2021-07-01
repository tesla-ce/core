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
import json

from django.utils import timezone

from tesla_ce.models.learner import get_missing_enrolment

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


def vle_check_learner_enrolment(vle, learner, activity, ic=True, enrolment=True):
    """
        The VLE checks the enrolment status of the learner.
        :param vle: VLE object
        :param learner: Learner object
        :param activity: Activity object
        :param ic: True if IC is expected to be accepted or False otherwise
        :param enrolment: True if enrolment is expected to be perfomed or False otherwise
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
            'vle_learner_uid': learner['uid']
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
        assert create_session_resp.status_code == 201

    # Check missing instruments
    return create_session_resp.data


def api_lapi_perform_enrolment(learner, launcher, missing):
    """
        The learner perform enrolment for missing instruments, sending data using LAPI and API
        :param learner: Learner object
        :param launcher: Launcher object
        :param missing: List of instruments with missing enrolment
    """
    pass


def vle_create_assessment_session(vle, learner, activity):
    """
        The VLE creates an assessment session for a learner for the activity
        :param vle: VLE object
        :param learner: Learner object
        :param activity: Activity object
        :return: New assessment session
    """
    assessment_session = None

    return assessment_session


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
    launcher_create_resp = client.post('/api/v2/vle/{}/launcher/'.format(vle_id),
                                       data=data)
    assert launcher_create_resp.status_code == 200

    launcher = launcher_create_resp.data
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

