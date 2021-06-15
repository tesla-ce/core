#  Copyright (c) 2021 Mireia Bellot
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
""" Test module for institution course groups management """
import logging

import pytest

import tests.utils

from tests.utils import getting_variables


@pytest.mark.django_db
def test_api_institution_course_groups(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Course Groups
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id
    intitution_course = institution_course_test_case['course']

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    # Institution Admin privileges
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)
    # TODO List Groups
    """ ---------------------------------------------------------------------
     LIST GROUPS:
        GET /api/v2/institution/(int: institution_id)/group/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
    Request Headers: Authorization - JWT with Institution Admin privileges
     """
    logging.info('\n1) LIST GROUPS --------------------------------------')
    # 666 TODO: find and add group ID instead of '/1'
    str_url = '/api/v2/institution/' + str(institution_id) + '/group/'
    str_response = 'RESPONSE id=' + str(institution_id) + ':'
    body = tests.utils.get_rest_api_client(rest_api_client, str_url,
                                           'List Groups', 'RESPONSE:', 200)

    # Ensure that no group exists
    assert body['count'] == 0

    pytest.skip("TODO")

    # 666 TODO list groups error (status 404?)


    # TODO Create a new Group
    # TODO Read group information
    # TODO Update group
    # TODO Delete group
    # TODO List courses in a group
    # TODO Add a course to a group
    # TODO Delete a course from a group
