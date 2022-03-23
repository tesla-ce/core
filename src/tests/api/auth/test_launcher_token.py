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
""" Test module for launcher token authentication """
import pytest


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
