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

#      VLE TEST
import pytest


@pytest.mark.django_db

def test_api_vle(rest_api_client):
    #666 plantilla codi: CANVIAR PROVIDER A VLE
    provider_response = rest_api_client.get('/api/v2/provider/')
    assert provider_response.status_code == 200

    providers = provider_response.json()
    print('\n**************** ADMIN ***********')
    print(providers)

#TODO VLE
#TODO Read VLE information
#TODO List Courses in a VLE
#TODO Create a new Course
#TODO Read Course information
#TODO Update Course information
#TODO Delete a Course
#TODO List Activities in a VLE Course
#TODO Create a new Activity
#TODO Read Activity information
#TODO Update Activity information
#TODO Delete an Activity
#TODO List Course learners --> TO BE DONE!
#TODO Add a learner to a course --> TO BE DONE!
#TODO Remove a learner from a course --> TO BE DONE!
#TODO List Course instructors --> TO BE DONE!
#TODO Add an instructor to a course --> TO BE DONE!
#TODO Remove an instructor from a course --> TO BE DONE!
#TODO TODO: Add assessment documentation --> TO BE DONE!



