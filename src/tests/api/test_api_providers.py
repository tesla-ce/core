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

#      PROVIDERS TEST
import pytest


@pytest.mark.django_db

def test_api_vle(rest_api_client):
    #666 plantilla codi: CANVIAR PROVIDER A el que toqui
    provider_response = rest_api_client.get('/api/v2/provider/')
    assert provider_response.status_code == 200

    providers = provider_response.json()
    print('\n**************** ADMIN ***********')
    print(providers)





