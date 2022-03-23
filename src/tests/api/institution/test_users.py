#  Copyright (c) 2021 Mireia Bellot
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
""" Test module for institution users management """
import pytest

from tests import auth_utils
from tests.conftest import get_random_string


def test_api_institution_users(rest_api_client, institution_course_test_case):
    """
        CRUD for institution users
    """
    # Set institution admin user.
    inst_admin = institution_course_test_case['user']
    inst_admin.institutionuser.inst_admin = True
    inst_admin.institutionuser.save()

    # Get the instution id
    inst_id = institution_course_test_case['institution'].id

    # Authenticate with institution admin
    client = auth_utils.client_with_user_obj(inst_admin)

    # Create a new user
    user_name = get_random_string(10)
    password = get_random_string(10)
    email = '{}@inst.tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'login_allowed': True,
        'is_active': True,
        'is_staff': False,
        'password': password,
        'password2': password
    }
    user_create_resp = client.post('/api/v2/institution/{}/user/'.format(inst_id), data=user_data, format='json')
    assert user_create_resp.status_code == 201

    # Ensure that this user can authenticate
    user_client = auth_utils.client_with_user_credentials(email, password)
    profile = auth_utils.get_profile(user_client)
    assert profile['institution'] is not None
    assert profile['institution']['id'] == inst_id
    assert len(profile['roles']) == 0
    assert profile['username'] == user_name
    assert profile['email'] == email
    assert profile['first_name'] == user_name[:5]
    assert profile['last_name'] == user_name[5:]

    # Grant administration privileges
    user_mod_resp = client.patch(
        '/api/v2/institution/{}/user/{}/'.format(inst_id, user_create_resp.data['id']),
        data={'inst_admin': True},
        format='json'
    )
    assert user_mod_resp.status_code == 200

    # Get the user profile again
    profile = auth_utils.get_profile(user_client)
    assert len(profile['roles']) == 1
    assert 'ADMIN' in profile['roles']

    # Try to grant global administration privileges
    user_mod_resp2 = client.patch(
        '/api/v2/institution/{}/user/{}/'.format(inst_id, user_create_resp.data['id']),
        data={'is_staff': True},
        format='json'
    )
    assert user_mod_resp2.status_code == 200

    # Get the user profile again
    profile = auth_utils.get_profile(user_client)
    assert len(profile['roles']) == 1
    assert 'ADMIN' in profile['roles']

    # Find for this user by email
    find_user_resp = client.get('/api/v2/institution/{}/user/?email={}'.format(inst_id, email))
    assert find_user_resp.status_code == 200
    assert find_user_resp.data['count'] == 1
    assert find_user_resp.data['results'][0]['id'] == profile['id']

    # Remove the user
    user_del_resp = client.delete(
        '/api/v2/institution/{}/user/{}/'.format(inst_id, user_create_resp.data['id'])
    )
    assert user_del_resp.status_code == 204

    # Ensure that this user does not exist
    find2_user_resp = client.get('/api/v2/institution/{}/user/?email={}'.format(inst_id, email))
    assert find2_user_resp.status_code == 200
    assert find2_user_resp.data['count'] == 0


@pytest.mark.django_db
def test_api_institution_user_filters(rest_api_client, institution_course_test_case):
    """
        Test filters for getting the users
    """
    # Set institution admin user.
    inst_admin = institution_course_test_case['user']
    inst_admin.institutionuser.inst_admin = True
    inst_admin.institutionuser.save()

    # Get the instution id
    inst_id = institution_course_test_case['institution'].id

    # Authenticate with institution admin
    client = auth_utils.client_with_user_obj(inst_admin)

    # Get the admin user by email
    get_user_by_email_resp = client.get('/api/v2/institution/{}/user/?email={}'.format(inst_id, inst_admin.email))
    assert get_user_by_email_resp.status_code == 200
    assert get_user_by_email_resp.data['count'] == 1
    assert get_user_by_email_resp.data['results'][0]['id'] == inst_admin.id

    # Filter users using one role
    get_user_by_role_resp = client.get('/api/v2/institution/{}/user/?roles=ADMIN'.format(inst_id))
    assert get_user_by_role_resp.status_code == 200
    assert get_user_by_role_resp.data['count'] == 1
    assert get_user_by_role_resp.data['results'][0]['id'] == inst_admin.id

    # Filter users using multiple roles
    inst_admin.institutionuser.legal_admin = True
    inst_admin.institutionuser.save()
    get_user_by_role2_resp = client.get('/api/v2/institution/{}/user/?roles=ADMIN&roles=LEGAL'.format(inst_id))
    assert get_user_by_role2_resp.status_code == 200
    assert get_user_by_role2_resp.data['count'] == 1
    assert get_user_by_role2_resp.data['results'][0]['id'] == inst_admin.id

    # Filter learners
    get_user_by_learner_role_resp = client.get('/api/v2/institution/{}/user/?roles=LEARNER'.format(inst_id))
    assert get_user_by_learner_role_resp.status_code == 200
    assert get_user_by_learner_role_resp.data['count'] == 1
    assert get_user_by_learner_role_resp.data['results'][0]['id'] == institution_course_test_case['learner'].id

    # Filter instructors
    get_user_by_instructor_role_resp = client.get('/api/v2/institution/{}/user/?roles=INSTRUCTOR'.format(inst_id))
    assert get_user_by_instructor_role_resp.status_code == 200
    assert get_user_by_instructor_role_resp.data['count'] == 1
    assert get_user_by_instructor_role_resp.data['results'][0]['id'] == institution_course_test_case['instructor'].id

    # Find for any admin
    inst_admin = institution_course_test_case['user']
    inst_admin.institutionuser.inst_admin = True
    inst_admin.institutionuser.send_admin = True
    inst_admin.institutionuser.data_admin = True
    inst_admin.institutionuser.legal_admin = True
    inst_admin.institutionuser.save()

    get_user_by_admins_roles_resp = client.get(
        '/api/v2/institution/{}/user/?roles=ADMIN&roles=LEGAL&roles=DATA&roles=SEND'.format(inst_id)
    )
    assert get_user_by_admins_roles_resp.status_code == 200
    assert get_user_by_admins_roles_resp.data['count'] == 1
    assert get_user_by_admins_roles_resp.data['results'][0]['id'] == inst_admin.id
