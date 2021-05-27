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


@pytest.mark.django_db
def test_api(rest_api_client):
    pass


def backup_test_api(rest_api_client):

    # Get the list of Institutions
    inst_response = rest_api_client.get('/api/v2/institution/')
    assert inst_response.status_code == 200

    institutions = inst_response.json()

    # Get the list of VLEs
    vle_response = rest_api_client.get('/api/v2/vle/')
    assert vle_response.status_code == 200

    # Get the list of Providers
    provider_response = rest_api_client.get('/api/v2/provider/')
    assert provider_response.status_code == 200

