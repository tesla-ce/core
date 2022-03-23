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
""" Test package for provider API """
import pytest
from tests.utils import get_module_auth_user


@pytest.mark.django_db
def test_api_provider(rest_api_client, providers):
    # Ensure the list of providers is not accessible
    provider_list_no_auth_response = rest_api_client.get('/api/v2/provider/')
    assert provider_list_no_auth_response.status_code == 403

    # Authenticate with Provider object
    rest_api_client.force_authenticate(user=get_module_auth_user(providers['fr']))

    # Check that is not possible to list the Providers
    provider_list_auth_response = rest_api_client.get('/api/v2/provider/')
    assert provider_list_auth_response.status_code == 403

    # Get Provider information
    provider_id = providers['fr'].id
    provider_info_auth_response = rest_api_client.get('/api/v2/provider/{}/'.format(provider_id))
    assert provider_info_auth_response.status_code == 200
    assert provider_info_auth_response.data['id'] == provider_id
