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
""" Test module for institution Instructor data management """
import logging

import pytest

import tests.utils


@pytest.mark.django_db
def test_api_institution_instructor(rest_api_client, institution_course_test_case):
    # Institution users need mail domain validation
    institution_course_test_case['institution'].mail_domain = 'tesla-ce.eu'
    institution_course_test_case['institution'].save()
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id

    # List Institution Instructor List
    logging.info('\n1) List Institution Instructor List --------------------------------------')
    # Set Institution Admin privileges
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/instructor/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Institution Instructor List ', str_message, 200)
    n_instructors = body['count']

    # Add a new Instructor to an institution
    logging.info('\n2) Add a new Instructor to an institution --------------------------------------')

    # 666 IntegrityError(1048, "Column 'last_name' cannot be null")
    str_data = {'uid': 'INSTRUCTOR_UID_TEST', 'first_name': 'INSTRUCTOR FIRST NAME',
                'last_name': 'INSTRUCTOR LAST NAME', 'email': 'email@tesla-ce.eu'}
    new_instructor_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                         'Add a new Instructor to an institution',
                                                         'RESPONSE: ', 201)

    #  Status 400: Validating email domain
    str_data = {'uid': 'INSTRUCTOR_UID_TEST', 'first_name': 'INSTRUCTOR FIRST NAME',
                'last_name': 'INSTRUCTOR LAST NAME', 'email': 'email@email.com'}
    tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                     'Add a new Instructor to an institution',
                                     'RESPONSE: ', 400)

    # Ensure number of instructors has increased
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Institution Instructor List ', str_message, 200)
    assert n_instructors + 1 == body['count']

    # Read Instructor information
    logging.info('\n3) Read Instructor information --------------------------------------')
    str_path = '/api/v2/institution/{}/instructor/{}/'.format(institution_id, new_instructor_id)
    str_response = 'RESPONSE Instructor ID={}:'.format(new_instructor_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Instructor information', str_response, 200)

    # Update Instructor information
    logging.info('\n4) Update Instructor information --------------------------------------')

    str_data = {'uid': 'INSTRUCTOR_UID_TEST', 'first_name': 'CHANGED_INSTRUCTOR FIRST NAME',
                'last_name': 'CHANGED_INSTRUCTOR LAST NAME', 'email': 'CHANGED_email@tesla-ce.eu'}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Update Instructor Information', str_response, 200)

    # Delete Instructor from an Institution
    logging.info('\n5) Delete Instructor from an Institution --------------------------------------')

    str_path = '/api/v2/institution/{}/instructor/{}/'.format(institution_id, new_instructor_id)
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete Instructor from an Institution', "RESPONSE: ", 204)

    # Ensure number of Instructors has decreased
    str_path = '/api/v2/institution/{}/instructor/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Institution Instructor List', str_message, 200)
    assert body['count'] == n_instructors

    # Ensure Instructors cannot be listed with normal user
    # Remove Institution Admin privileges
    institution_user.inst_admin = False
    institution_user.send_admin = False
    institution_user.legal_admin = False
    institution_user.data_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    logging.info('\n6) Listing Institution Instructor List with invalid user  --------------------------------------')
    str_path = '/api/v2/institution/{}/instructor/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'List Institution Instructor List with invalid user', str_message, 403)

    # Add an Instructor to an Institution with invalid user
    logging.info('\n7) Add an Instructor to an Institution with invalid user  --------------------------------------')
    str_data = {'username': 'USERNAME_TEST', 'email': 'email@email.com'}
    tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                     'Add an Instructor to an Institution with invalid user', 'RESPONSE: ', 403)
