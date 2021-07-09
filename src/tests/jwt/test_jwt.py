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
import pytest

from tesla_ce.lib import TeslaVaultException


@pytest.mark.django_db
def test_create_learner_token(api_client, lapi_client, institution_course_test_case):
    assert api_client is not None
    assert lapi_client is not None

    learner = institution_course_test_case['learner']
    if learner is None:
        pytest.skip('No learners in DB')

    # Get learner object
    learner = learner.institutionuser.learner

    # Generate the token in the API
    token = api_client.get_learner_token_pair(learner, scope='/api/*')
    assert token is not None
    assert 'access_token' in token
    assert 'refresh_token' in token

    # Check that this token is valid for API
    validation_api = api_client.validate_token(token['access_token'])
    assert validation_api is not None
    assert isinstance(validation_api, dict)
    assert validation_api['group'] == 'learners'

    # Check that this token is valid for Learners API
    validation_lapi = lapi_client.validate_token(token['access_token'])
    assert validation_lapi is not None
    assert isinstance(validation_lapi, dict)
    assert validation_lapi['group'] == 'learners'

    # Ensure that lapi cannot create learner tokens
    try:
        lapi_client.get_learner_token_pair(learner, scope='/api/*')
        pytest.fail('LAPI Module is able to generate learner tokens')
    except TeslaVaultException:
        pass


@pytest.mark.django_db
def test_create_instructor_token(api_client, lapi_client, institution_course_test_case):
    assert api_client is not None
    assert lapi_client is not None

    instructor = institution_course_test_case['instructor']
    if instructor is None:
        pytest.skip('No instructors in DB')

    # Get instructor object
    instructor = instructor.institutionuser.instructor
    scope = {
        'activity': 'my_activity'
    }

    # Generate the token in the API
    token = api_client.get_instructor_token(instructor.email, scope)
    assert token is not None

    # Check that this token is valid for API
    validation_api = api_client.validate_token(token)
    assert validation_api is not None
    assert isinstance(validation_api, dict)
    assert validation_api['group'] == 'instructors'

    # Ensure that lapi cannot create instructor tokens
    try:
        lapi_client.get_instructor_token(instructor.email, scope)
        pytest.fail('LAPI Module is able to generate instructor tokens')
    except TeslaVaultException:
        pass


@pytest.mark.django_db
def test_create_user_token(api_client, lapi_client, institution_test_case):
    assert api_client is not None
    assert lapi_client is not None

    user = institution_test_case['user'].institutionuser
    if user is None:
        pytest.skip('No institution users in DB')

    scope = ['/api/*']

    # Generate the token in the API
    token = api_client.get_user_token_pair(user=user, scope=scope)
    assert token is not None
    assert 'access_token' in token
    assert 'refresh_token' in token

    # Check that this token is valid for API
    validation_api = api_client.validate_token(token['access_token'])
    assert validation_api is not None
    assert isinstance(validation_api, dict)
    assert validation_api['group'] == 'users'

    # Ensure that lapi cannot create users tokens
    try:
        lapi_client.get_user_token_pair(user=user, scope=scope)
        pytest.fail('LAPI Module is able to generate user tokens')
    except TeslaVaultException:
        pass


@pytest.mark.django_db
def test_create_module_token(api_client, lapi_client):
    assert api_client is not None
    assert lapi_client is not None

    scope = {
    }

    # Generate the token in the API
    api_token = api_client.get_module_token(scope)
    assert api_token is not None

    # Check that this token is valid for API
    validation_api = api_client.validate_token(api_token)
    assert validation_api is not None
    assert isinstance(validation_api, dict)
    assert validation_api['group'].startswith('module_')
    assert validation_api['sub'] == 'api'

    # Check that other modules cannot generate tokens
    try:
        lapi_client.get_module_token(scope)
        pytest.fail('Dashboards Module is able to generate module tokens')
    except TeslaVaultException:
        pass

    # Generate the token for LAPI
    lapi_token = api_client.get_module_token(scope, module_id='lapi')

    # Check that this token is valid for API
    validation_api = api_client.validate_token(lapi_token)
    assert validation_api is not None
    assert isinstance(validation_api, dict)
    assert validation_api['group'].startswith('module_')
    assert validation_api['sub'] == 'lapi'

    # Check that this token is valid for LAPI
    validation_lapi = lapi_client.validate_token(lapi_token)
    assert validation_lapi is not None
    assert isinstance(validation_lapi, dict)
    assert validation_lapi['group'].startswith('module_')
    assert validation_lapi['sub'] == 'lapi'
