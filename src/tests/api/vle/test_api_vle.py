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
""" Test package for VLE API """
import pytest
from tests.utils import get_module_auth_user

@pytest.mark.django_db
def test_api_vle(rest_api_client, institution_course_test_case):
    # Ensure VLE list is not allowed
    vle_list_no_auth_response = rest_api_client.get('/api/v2/vle/')
    assert vle_list_no_auth_response.status_code == 403

    # Authenticate with VLE object
    rest_api_client.force_authenticate(user=get_module_auth_user(institution_course_test_case['vle']))

    # Check that is not possible to list the VLEs
    vle_list_auth_response = rest_api_client.get('/api/v2/vle/')
    assert vle_list_auth_response.status_code == 403

    # Get VLE information
    vle_id = institution_course_test_case['vle'].id
    vle_info_auth_response = rest_api_client.get('/api/v2/vle/{}/'.format(vle_id))
    assert vle_info_auth_response.status_code == 200
    assert vle_info_auth_response.data['id'] == vle_id

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



