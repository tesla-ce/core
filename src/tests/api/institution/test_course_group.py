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
from tesla_ce.models import CourseGroup, Course

from tests.utils import getting_variables


@pytest.mark.django_db
def test_api_institution_course_groups(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Course Groups
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
    """ ---------------------------------------------------------------------
     LIST GROUPS:
        GET /api/v2/institution/(int: institution_id)/group/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
    Request Headers: Authorization - JWT with Institution Admin privileges
     """
    logging.info('\n1) LIST GROUPS --------------------------------------')
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/'
    str_response = 'RESPONSE id=' + str(institution_id) + ':'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)

    # Ensure that no group exists
    assert body['count'] == 0

    # TODO? List group errors: status 404 institution not found

    # Create a new Group
    """ ---------------------------------------------------------------------
    CREATE A NEW GROUP:
        POST /api/v2/institution/(int: institution_id)/group/
        Request JSON Object
            parent (int) – Id of the parent group. Null if this group is not in another group.
            name (string) – Name of the group.
            description (string) – Description of the group.
        Status Codes:
            201 Created – Created
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n2) CREATE A NEW GROUP --------------------------------------')
    str_data = {'parent': '', 'name': 'TEST_GROUP', 'description': 'This is a test group'}
    new_group_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                    'Create a new group', 'RESPONSE: ', 201)

    # List groups
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)

    # Ensure group exists
    n_groups = body['count']
    assert n_groups > 0

    # Testing groups hierarchy (nested object)
    # 666: fails
    ''' 666
    hierarchy_test_group = CourseGroup.objects.create(
        institution=institution,
        name='NEW_LEVEL_TEST_GROUP',
        description='This is a NEW LEVEL group.',
        parent=test_group_course
    )
    '''
    # str_data = {'parent': new_group_id, 'name': 'TEST_GROUP', 'description': 'This is a test group'}
    # new_second_group_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
    #                                                        'Create a new level group',
    #                                                        'RESPONSE: ', 201)

    # TODO? Create a new group errors: status 400 and 404

    # Read group information
    """ ---------------------------------------------------------------------
     READ GROUP INFORMATION:
        GET /api/v2/institution/(int: institution_id)/group/(int: group_id)/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Group not found
    Request Headers: Authorization - JWT with Institution Admin privileges
     """
    logging.info('\n3) READ GROUP INFORMATION --------------------------------------')
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/'
    str_response = 'RESPONSE group id=' + str(new_group_id) + ':'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'Read Group Information', 'RESPONSE:', 200)

    # TODO? Read group information errors: status 404 institution and/or group not found

    # Update group
    """ ---------------------------------------------------------------------
    UPDATE GROUP:
        PUT /api/v2/institution/(int: institution_id)/group/(int: group_id)/
        Status Codes:
            200 OK – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
            404 Not Found – Group not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n4) UDPATE GROUP INFORMATION --------------------------------------')
    # str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/'
    str_data = {'name': 'CHANGED_TEST_GROUP', 'description': 'This is a CHANGED TEXT FOR THE test group'}

    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Update group', 'RESPONSE: ', 200)

    # TODO? Read group information errors: status 400 and 404

    # Delete group
    """ ---------------------------------------------------------------------
    DELETE GROUP:
        DELETE /api/v2/institution/(int: institution_id)/group/(int: group_id)/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Group not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n5) DELETE GROUP --------------------------------------')
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/'
    # 666 check source https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.7
    # A successful response SHOULD be 200 (OK) if the response includes an entity describing the status,
    # 202 (Accepted) if the action has not yet been enacted, or 204 (No Content) if the action has been enacted
    # but the response does not include an entity.
    # 666 ADD THOSE STATUS TO DOC?
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete group', "RESPONSE: ", 204)
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Groups', 'RESPONSE:', 200)
    logging.info(body)
    # Ensure number of groups has decreased
    assert body['count'] == (n_groups - 1)

    # TODO? Read group information errors: status 400 and 404

    pytest.skip("TODO")

    # List courses in a group
    """ ---------------------------------------------------------------------
    LIST COURSES IN A GROUP:
        GET /api/v2/institution/(int: institution_id)/group/(int: group_id)/course/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Group not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n6) LIST COURSES IN A GROUP --------------------------------------')
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/course/'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Courses in a Group', 'RESPONSE:', 200)
    n_courses = body['count']

    # TODO? Read group information errors: status 400 and 404

    # Add a course to a group: XEVI 666
    """ ---------------------------------------------------------------------
    ADD A COURSE TO A GROUP:
        POST /api/v2/institution/(int: institution_id)/group/(int: group_id)/course/
        Request JSON Object:
            id (int) – Course ID.
        Status Codes:
            200 OK – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
            404 Not Found – Group not found
            404 Not Found – Course not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n7) ADD A COURSE TO A GROUP --------------------------------------')
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/course/'
    course_code = institution_course_test_case['course'].code
    course_vle = institution_course_test_case['course'].vle.name
    course_vle_course_id = institution_course_test_case['course'].vle_course_id
    '''
    new_course = Course.objects.create(
        model='Course VLE',
        code="Course code.",
        vle_course_id='Course id on the VLE')
    '''

    logging.info(course_code)
    logging.info(course_vle)
    logging.info(course_vle_course_id)

    # new_course = {'model':'Course VLE TEST', 'code': 'Course code TEST', 'vle_course_id': 'Course id TEST on the VLE'}
    # new_course = {'model': course_vle, 'code': course_code, 'vle_course_id': course_vle_course_id}
    new_course = {'model': course_vle, 'code': course_code, 'vle_course_id': course_vle_course_id}

    new_course_id = tests.utils.post_rest_api_client(rest_api_client, str_path, new_course,
                                                     'Add a Course to a Group', 'RESPONSE: ', 200)

    # TODO Delete a course from a group
    """ ---------------------------------------------------------------------
    DELETE A COURSE FROM A GROUP:
        DELETE /api/v2/institution/(int: institution_id)/group/(int: group_id)/course/(int: course_id)/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Group not found
            404 Not Found – Course not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n8) DELETE A COURSE FROM A GROUP --------------------------------------')
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/course/'
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete a Course from a Group', "RESPONSE: ", 200)
    # str_path = '/api/v2/institution/' + str(institution_id) + '/group/'
    str_path = '/api/v2/institution/' + str(institution_id) + '/group/' + str(new_group_id) + '/course/'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Courses in a Group', 'RESPONSE:', 200)
    logging.info(body)
    # Ensure number of groups has decreased
    assert body['count'] == (n_groups - 1)

