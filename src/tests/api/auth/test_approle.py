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
""" Test module for approle authentication """
import pytest


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
