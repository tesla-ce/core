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


@pytest.mark.django_db
def test_api_institution_course_groups(rest_api_client, user_global_admin, institution_course_test_case):
    institution_user = institution_course_test_case['user'].institutionuser
    institution = institution_course_test_case['institution']
    institution_id = institution.id

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    # Institution Admin privileges
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    # List Groups
    logging.info('\n1) LIST GROUPS --------------------------------------')
    str_path = '/api/v2/institution/{}/group/'.format(institution_id)
    str_response = 'RESPONSE id={}:'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', str_response, 200)
    # Ensure that no group exists
    assert body['count'] == 0

    # Create a new Group
    logging.info('\n2) CREATE A NEW GROUP --------------------------------------')
    str_data = {'parent': '', 'name': 'TEST_GROUP', 'description': 'This is a test group'}
    new_group_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                    'Create a new group', 'RESPONSE: ', 201)

    # List groups
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)

    # Ensure group exists
    n_groups = body['count']
    assert n_groups == 1

    # Create a new nested Group
    logging.info('\n2) CREATE A NEW NESTED GROUP --------------------------------------')
    str_data = {'parent': new_group_id , 'name': 'TEST_GROUP', 'description': 'This is a test group'}
    new_subgroup_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                       'Create a new nested group', 'RESPONSE: ', 201)

    # List groups
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)

    # Ensure group exists
    n_groups = body['count']
    assert n_groups == 2

    # Filter root groups (parent is None)
    body = tests.utils.get_rest_api_client(rest_api_client, '{}?parent={}'.format(str_path, -1),
                                           'List Root Groups', 'RESPONSE:', 200)
    assert body['count'] == 1
    assert body['results'][0]['id'] == new_group_id

    # Filter child groups
    body = tests.utils.get_rest_api_client(rest_api_client, '{}?parent={}'.format(str_path, new_group_id),
                                           'List Child Groups', 'RESPONSE:', 200)
    assert body['count'] == 1
    assert body['results'][0]['id'] == new_subgroup_id


    # Read group information
    logging.info('\n3) READ GROUP INFORMATION --------------------------------------')
    str_path = '/api/v2/institution/{}/group/{}/'.format(institution_id, new_group_id)
    str_response = 'RESPONSE group id={}:'.format(new_group_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Group Information', str_response, 200)

    # Update group data
    logging.info('\n4) UDPATE GROUP INFORMATION --------------------------------------')
    str_data = {'name': 'CHANGED_TEST_GROUP', 'description': 'This is a CHANGED TEXT FOR THE test group'}

    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Update group', 'RESPONSE: ', 200)

    # Delete root group
    logging.info('\n5) DELETE ROOT GROUP --------------------------------------')
    str_path = '/api/v2/institution/{}/group/{}/'.format(institution_id, new_group_id)
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete group', "RESPONSE: ", 204)
    str_path = '/api/v2/institution/{}/group/'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)
    logging.info(body)

    # Ensure that the root group and child group are removed
    assert body['count'] == 0


@pytest.mark.django_db
def test_api_institution_course_group_courses(rest_api_client, user_global_admin, institution_course_test_case):
    institution_user = institution_course_test_case['user'].institutionuser
    institution = institution_course_test_case['institution']
    institution_id = institution.id

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    # Institution Admin privileges
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    # Create a new Group
    logging.info('\n2) CREATE A NEW GROUP --------------------------------------')
    str_path = '/api/v2/institution/{}/group/'.format(institution_id)
    str_data = {'parent': '', 'name': 'TEST_GROUP', 'description': 'This is a test group'}
    new_group_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                    'Create a new group', 'RESPONSE: ', 201)

    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)
    assert body['count'] == 1

    # List courses in a group
    logging.info('\n6) LIST COURSES IN A GROUP --------------------------------------')
    str_path = '/api/v2/institution/{}/group/{}/course/'.format(institution_id, new_group_id)

    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Courses in a Group', 'RESPONSE:', 200)

    # Ensure no courses in a new group by default
    assert body['count'] == 0

    # Add a new course
    logging.info('\n7) ADD A COURSE TO A GROUP --------------------------------------')
    str_path = '/api/v2/institution/{}/group/{}/course/'.format(institution_id, new_group_id)
    course_id = institution_course_test_case['course'].id
    tests.utils.post_rest_api_client(rest_api_client, str_path, {'id': course_id},
                                     'Add a Course to a Group', 'RESPONSE: ', 201)

    # List and check number of courses in a group has increased.
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Courses in a Group', 'RESPONSE:', 200)
    assert body['count'] == 1
    assert body['results'][0]['id'] == course_id

    # Delete a course from a group
    logging.info('\n8) DELETE A COURSE FROM A GROUP --------------------------------------')
    str_path_course = '/api/v2/institution/{}/group/{}/course/{}/'.format(institution_id, new_group_id, course_id)
    tests.utils.delete_rest_api_client(rest_api_client, str_path_course,
                                       'Delete a Course from a Group', "RESPONSE: ", 204)
    tests.utils.get_rest_api_client(rest_api_client, str_path_course,
                                    'Show removed course', 'RESPONSE:', 404)

    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Courses in a Group', 'RESPONSE:', 200)
    assert body['count'] == 0
