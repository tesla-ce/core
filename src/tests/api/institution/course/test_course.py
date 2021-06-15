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
""" Test module for institution course management """
import logging

import pytest

import tests.utils


@pytest.mark.django_db
def test_api_institution_course_list(rest_api_client, user_global_admin, institution_course_test_case):
    # Get general parameters
    institution_id = institution_course_test_case['institution'].id
    courses_url = '/api/v2/institution/' + str(institution_id) + '/course/'

    # Get the list of courses for the global admin
    user_global_admin.is_staff = True
    user_global_admin.save()
    rest_api_client.force_authenticate(user=user_global_admin)
    global_admin_resp = tests.utils.get_rest_api_client(
        rest_api_client, courses_url, 'List Courses Global Admin', 'RESPONSE:', 200)
    assert global_admin_resp['count'] == 1

    # Get the list of courses for an Institution Admin
    institution_user = institution_course_test_case['user'].institutionuser
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)
    inst_admin_resp = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                      'List Courses Inst Admin', 'RESPONSE:', 200)
    assert inst_admin_resp['count'] == 1

    # Get the list of courses for a normal Institution User not belonging to any course
    institution_user = institution_course_test_case['user'].institutionuser
    institution_user.inst_admin = False
    institution_user.data_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)
    inst_admin_resp = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                      'List Courses Inst User', 'RESPONSE:', 200)
    assert inst_admin_resp['count'] == 0





