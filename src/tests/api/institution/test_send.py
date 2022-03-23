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
""" Test module for institution SEND data management """
import logging

import pytest

import tests.utils


@pytest.mark.django_db
def test_api_institution_send(rest_api_client, institution_course_test_case):
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id

    # List SEND Categories
    logging.info('\n1) List SEND Categories --------------------------------------')
    # Set Institution Admin/SEND privileges
    institution_user.send_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/send/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List SEND categories', str_message, 200)
    n_send = body['count']
    assert n_send == 0

    # Create a new SEND Category
    logging.info('\n2) Create a new SEND Category --------------------------------------')
    data = {'enabled_options': ['text_to_speech', 'big_fonts', 'high_contrast'],
            'disabled_instruments': [1, 2, 3, 4, 5]}

    str_data = {'parent': '',
                'description': 'SEND Category for TESTING purposes',
                'data': data}
    new_send_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                   'Create a new SEND Category', 'RESPONSE: ', 201)

    # Ensure number of categories has increased
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List SEND categories', str_message, 200)
    assert n_send + 1 == body['count']

    # Read SEND Category information
    logging.info('\n3) Read SEND Category information --------------------------------------')

    str_path = '/api/v2/institution/{}/send/{}/'.format(institution_id, new_send_id)
    str_response = 'RESPONSE SEND ID={}:'.format(new_send_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read SEND Category information', str_response, 200)

    # Update SEND Category
    logging.info('\n4) Update SEND Category --------------------------------------')

    str_data = {'description': 'CHANGED SEND Category for TESTING purposes'}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Update SEND Category', str_response, 200)

    # Delete SEND Category
    logging.info('\n5) Delete SEND Category --------------------------------------')

    str_path = '/api/v2/institution/{}/send/{}/'.format(institution_id, new_send_id)
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete SEND Category', "RESPONSE: ", 204)

    # Ensure number of SEND categories has decreased
    str_path = '/api/v2/institution/{}/send/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List SEND categories', str_message, 200)
    assert body['count'] == n_send

    # Ensure SEND categories cannot be listed with normal user
    # Remove Institution SEND privileges
    institution_user.inst_admin = False
    institution_user.send_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/send/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'List SEND categories with invalid user', str_message, 403)

    # Create a new SEND Category with invalid user
    logging.info('\n2) Create a new SEND Category with invalid user  --------------------------------------')
    str_data = {'description': 'SEND Category for TESTING purposes',
                'data': ''}
    tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                     'Create a new SEND Category with invalid user', 'RESPONSE: ', 403)
