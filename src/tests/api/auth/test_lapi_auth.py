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
""" Test module for LAPI token based authentication """
import pytest


@pytest.mark.django_db
def test_lapi_authentication(rest_api_client, api_client, institution_course_test_case):

    # Get a launcher token for learner
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

    # Assign credentials
    token = resp_lapi_token.data['access_token']
    rest_api_client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))

    # Use token to access LAPI
    lapi_call_resp = rest_api_client.get('/lapi/v1/profile/{}/{}/'.format(
        institution_course_test_case['learner'].institutionuser.institution_id,
        institution_course_test_case['learner'].institutionuser.learner.learner_id
    ))
    assert lapi_call_resp.status_code == 200
