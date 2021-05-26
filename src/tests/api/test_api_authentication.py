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
""" Authentication API test """
import pytest


def check_roles(profile, roles=None):

    assert 'roles' in profile

    available_roles = ['GLOBAL_ADMIN', 'LEARNER', 'INSTRUCTOR', 'ADMIN', 'SEND', 'LEGAL', 'DATA']

    if roles is None:
        roles = []

    for role in roles:
        available_roles.remove(role)

    for role in roles:
        assert role in profile['roles']
        if 'institution' in profile and profile['institution'] is not None:
            if role == 'GLOBAL_ADMIN':
                assert role not in profile['institution']['roles']
            else:
                assert role in profile['institution']['roles']

    for role in available_roles:
        assert role not in profile['roles']
        if 'institution' in profile and profile['institution'] is not None:
            assert role not in profile['institution']['roles']


@pytest.mark.django_db
def get_profile(rest_api_client, token):
    """
        Get authenticated user profile
        :param rest_api_client: API client
        :param token: Access token
        :return: Returned profile
    """
    rest_api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
    profile_resp = rest_api_client.get('/api/v2/auth/profile')
    rest_api_client.credentials()

    return profile_resp


@pytest.mark.django_db
def test_api_authentication_approle(rest_api_client, api_client, institution_course_test_case, providers):

    # Generate a approle for a VLE
    vle_creds = api_client.vault.register_vle(institution_course_test_case['vle'])

    # Generate a approle for a Provider
    provider_creds = api_client.vault.register_provider(providers['fr'])

    # Authenticate using vle credentials
    resp_vle = rest_api_client.post('/api/v2/auth/approle', data=vle_creds)

    assert resp_vle is not None
    assert resp_vle.status_code == 200
    assert resp_vle.data['pk'] == institution_course_test_case['vle'].id
    assert resp_vle.data['module'].startswith('vle_')
    assert resp_vle.data['type'] == 'vle'

    validation_jwt_vle = api_client.validate_token(resp_vle.data['token']['access_token'])
    assert validation_jwt_vle is not None
    assert isinstance(validation_jwt_vle, dict)
    assert validation_jwt_vle['group'].startswith('module_')
    assert validation_jwt_vle['pk'] == institution_course_test_case['vle'].id
    assert validation_jwt_vle['type'] == 'vle'

    # Authenticate using provider credentials
    resp_provider = rest_api_client.post('/api/v2/auth/approle', data=provider_creds)

    assert resp_provider is not None
    assert resp_provider.status_code == 200
    assert 'pk' in resp_provider.data
    assert resp_provider.data['module'].startswith('provider_')
    assert resp_provider.data['type'] == 'provider'

    validation_jwt_provider = api_client.validate_token(resp_provider.data['token']['access_token'])
    assert validation_jwt_provider is not None
    assert isinstance(validation_jwt_provider, dict)
    assert validation_jwt_provider['group'].startswith('module_')
    assert 'pk' in validation_jwt_provider
    assert validation_jwt_provider['type'] == 'provider'


@pytest.mark.django_db
def test_api_authentication_launchertoken(rest_api_client, api_client, lapi_client, institution_course_test_case):

    # Generate a token for dashboards
    dash_token = api_client.get_launcher_token('DASHBOARD', institution_course_test_case['user'].institutionuser)

    assert dash_token is not None
    assert 'id' in dash_token
    assert 'token' in dash_token

    # Authenticate using the token
    resp_dash_token = rest_api_client.post('/api/v2/auth/token', data=dash_token)

    assert resp_dash_token is not None
    assert resp_dash_token.status_code == 200
    assert 'access_token' in resp_dash_token.data
    assert 'refresh_token' in resp_dash_token.data

    # Authenticate using the token
    validation_jwt_dash = api_client.validate_token(resp_dash_token.data['access_token'])

    assert validation_jwt_dash is not None
    assert validation_jwt_dash['pk'] == institution_course_test_case['user'].institutionuser.id

    # Generate a token for LAPI
    try:
        api_client.get_launcher_token('LAPI', institution_course_test_case['user'].institutionuser)
        pytest.fail('No learner users are able to request token for LAPI')
    except Exception:
        pass

    lapi_token = api_client.get_launcher_token('LAPI', institution_course_test_case['learner'].institutionuser)

    assert lapi_token is not None
    assert 'id' in lapi_token
    assert 'token' in lapi_token

    # Authenticate using the token
    resp_lapi_token = rest_api_client.post('/api/v2/auth/token', data=lapi_token)

    assert resp_lapi_token is not None
    assert resp_lapi_token.status_code == 200
    assert 'access_token' in resp_lapi_token.data
    assert 'refresh_token' in resp_lapi_token.data

    # Authenticate using the token for LAPI
    validation_jwt_lapi = lapi_client.validate_token(resp_lapi_token.data['access_token'])

    assert validation_jwt_lapi is not None
    assert validation_jwt_lapi['pk'] == institution_course_test_case['learner'].institutionuser.id

    # Authenticate using the token for API
    validation_jwt_api = api_client.validate_token(resp_lapi_token.data['access_token'])

    assert validation_jwt_api is not None
    assert validation_jwt_api['pk'] == institution_course_test_case['learner'].institutionuser.id

    # Request token for API
    try:
        api_client.get_launcher_token('API', institution_course_test_case['user'].institutionuser)
        pytest.fail('Launcher token for API should not be allowed')
    except Exception:
        pass


@pytest.mark.django_db
def test_api_authentication_userpass(rest_api_client, api_client, institution_test_case):
    pass


@pytest.mark.django_db
def test_api_authentication_profile(rest_api_client, api_client, institution_course_test_case,
                                    providers, user_global_admin):

    # Test profile without authentication
    noauth_resp = rest_api_client.get('/api/v2/auth/profile')
    assert noauth_resp.status_code == 401

    # Get vle credentials
    vle_token = api_client.get_module_token(
        scope={},
        module_id='vle_{}'.format(str(institution_course_test_case['vle'].id).zfill(3))
    )

    vle_profile_resp = get_profile(rest_api_client, vle_token)
    assert vle_profile_resp.status_code == 403

    # Get provider credentials
    provider_token = api_client.get_module_token(
        scope={},
        module_id='provider_{}'.format(str(providers['fr'].id).zfill(3))
    )

    vle_profile_resp = get_profile(rest_api_client, provider_token)
    assert vle_profile_resp.status_code == 403

    # Get global admin token
    global_admin_token = api_client.get_admin_token_pair(user_global_admin, {})
    assert global_admin_token is not None
    assert 'access_token' in global_admin_token
    global_admin_profile_resp = get_profile(rest_api_client, global_admin_token['access_token'])
    assert global_admin_profile_resp.status_code == 200
    check_roles(global_admin_profile_resp.data, roles=['GLOBAL_ADMIN'])

    # Get institution user token
    inst_user_token = api_client.get_user_token_pair(institution_course_test_case['user'].institutionuser, {})
    assert inst_user_token is not None
    assert 'access_token' in inst_user_token
    inst_user_profile_resp = get_profile(rest_api_client, inst_user_token['access_token'])
    assert inst_user_profile_resp.status_code == 200
    assert 'institution' in inst_user_profile_resp.data
    check_roles(inst_user_profile_resp.data, roles=[])

    # Get institution admin token
    admin_user = institution_course_test_case['user'].institutionuser
    admin_user.inst_admin = True
    admin_user.data_admin = True
    admin_user.legal_admin = True
    admin_user.send_admin = True
    admin_user.save()

    inst_admin_user_token = api_client.get_user_token_pair(admin_user, {})
    assert inst_admin_user_token is not None
    assert 'access_token' in inst_admin_user_token
    inst_admin_user_profile_resp = get_profile(rest_api_client, inst_admin_user_token['access_token'])
    assert inst_admin_user_profile_resp.status_code == 200
    assert 'institution' in inst_admin_user_profile_resp.data
    check_roles(inst_admin_user_profile_resp.data, roles=['ADMIN', 'SEND', 'LEGAL', 'DATA'])

    # Get institution learner token
    learner_user = institution_course_test_case['learner'].institutionuser.learner

    inst_learner_user_token = api_client.get_user_token_pair(learner_user, {})
    assert inst_learner_user_token is not None
    assert 'access_token' in inst_learner_user_token
    inst_learner_user_profile_resp = get_profile(rest_api_client, inst_learner_user_token['access_token'])
    assert inst_learner_user_profile_resp.status_code == 200
    assert 'institution' in inst_learner_user_profile_resp.data
    check_roles(inst_learner_user_profile_resp.data, roles=['LEARNER'])

    # Get institution instructor token
    instructor_user = institution_course_test_case['instructor'].institutionuser.instructor

    inst_instructor_user_token = api_client.get_user_token_pair(instructor_user, {})
    assert inst_instructor_user_token is not None
    assert 'access_token' in inst_learner_user_token
    inst_instructor_user_profile_resp = get_profile(rest_api_client, inst_instructor_user_token['access_token'])
    assert inst_instructor_user_profile_resp.status_code == 200
    assert 'institution' in inst_instructor_user_profile_resp.data
    check_roles(inst_instructor_user_profile_resp.data, roles=['INSTRUCTOR'])
