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
""" TeSLA CE Institution Administrator actions for Use Case tests """
from django.utils import timezone

from tests import auth_utils
from tests.conftest import get_random_string


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


def api_create_ic(admin, version):
    """
        A legal administrator of the institution creates the Informed Consent using the API
        :param admin: Credentials for a user with legal administration rights
        :param version: Version of the Informed Consent
    """
    # Authenticate with admin credentials
    client = auth_utils.client_with_user_credentials(admin['email'], admin['password'])

    # Get the user profile
    profile = auth_utils.get_profile(client)

    # Create an IC
    institution_id = profile['institution']['id']
    ic_data = {
        'version': version,
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


def api_create_send_categories(admin, disabled_inst=None):
    """
        A SEND administrator of the institution defines the SEND categories using the API
        :param admin: Credentials for a user with SEND administration rights
        :param disabled_inst: List of instruments to disable
    """
    if disabled_inst is None:
        disabled_inst = []

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
