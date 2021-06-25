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
""" Test module for institution management """
import logging

import pytest

import tests.utils

from tests.utils import getting_variables


@pytest.mark.django_db
def test_api_institution_learner(rest_api_client, user_global_admin, institution_course_test_case):
    """

    INSTITUTION TEST: LEARNER
       1) List learners
       2) Create a new learner
       3) Read new learner information
       4) Update new learner
       5) Delete new learner
       TODO: Accept an informed consent for a learner
       TODO: Reject current Informed Consent of a learner
       TODO: Add SEND category to a learner
       TODO: Read SEND categories assigned to a learner
       TODO: Remove a SEND Category from a learner

    """
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id
    learner = institution_course_test_case['learner']
    learner_user = learner.institutionuser
    instructor_user = institution_course_test_case['instructor'].institutionuser

    # 666?
    # Global Administration privileges
    # user_global_admin.is_staff = True
    # user_global_admin.save()

    # Set global admin user.
    # rest_api_client.force_authenticate(user=user_global_admin)

    logging.info('\nTESTING INSTITUTIONS: Learners *********************************************')

    # Get the list of Institutions
    """ ---------------------------------------------------------------------
    LIST LEARNERS:
       GET /api/v2/institution/(int: institution_id)/learner
       Status Codes:
           200 OK – Ok
           404 Not Found – Institution not found
    Request Headers: Authorization - JWT with Institution Admin/Instructor privileges
    """
    logging.info('\n1) LIST LEARNERS --------------------------------------')
    # institution_user.legal_admin = False
    # institution_user.save()
    # rest_api_client.force_authenticate(user=institution_user)
    instructor_user.legal_admin = False
    instructor_user.save()
    rest_api_client.force_authenticate(user=instructor_user)

    str_path = '/api/v2/institution/{}/learner/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List learners', str_message, 200)
    n_learners = body['count']
    variables = getting_variables(body, institution_id)

    if variables['n_institution'] > 0:
        tests.utils.check_pagination(rest_api_client, body)
        args = [['List Learners'], ['ID FIRST LEARNER: ', variables['id_first_institution']],
                ['NUMBER OF LEARNERS:', variables['n_institution']],
                ['INSTITUTION ID TEST', institution_id],
                ['ID NON EXISTING INSTITUTION:', variables['id_non_existing_institution']]]
    else:
        args = [['List Institutions'], ['Empty Institutions list. Reading first Institution test will be skipped.']]

    tests.utils.print_log(args)

    # 2) Create a new learner
    """ ---------------------------------------------------------------------
    CREATE A NEW LEARNER:
        POST /api/v2/institution/(int:institution_id)/learner
        Request JSON Object
            uid (string) – Unique ID of this learner in the institution.
            email (string) – Email of the learner. If institution mail_domain is provided, 
                             this email must be in this domain.
            first_name (string) – First name of the learner.
            last_name (string) – Last name of the learner.
        Status Codes:
            201 Created – Created
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    # 666? whyy instructor user works if it does not have admin privileges?
    # 666? It works properly with "legal_admin = False"
    instructor_user.legal_admin = True
    instructor_user.save()
    rest_api_client.force_authenticate(user=instructor_user)

    logging.info('\n2) CREATE A NEW LEARNER --------------------------------------')
    str_data = {'uid': 'LEARNER_UID', 'email': 'mail_test@tesla-ce.eu',
                'first_name': 'TEST_LEARNER_NAME',
                'last_name': 'TEST_LEARNER_LASTNAME'}
    new_learner_id = tests.utils.post_rest_api_client(rest_api_client, str_path, str_data,
                                                      'Create a new learner', 'RESPONSE: ', 201)

    #  # Ensure number of learners has increased
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List learners', 'RESPONSE:', 200)
    assert n_learners + 1 == body['count']
    # TODO? Create a new learner errors

    # 3) Read learner information
    """ ---------------------------------------------------------------------
    READ LEARNER INFORMATION:
    GET /api/v2/institution/(int: institution_id)/learner/(int: learner_id)
    Status Codes:
        200 OK – Ok
        404 Not Found – Institution not found
        404 Not Found – Learner not found
    Privileges: Institution Admin/Instructor privileges
    """
    logging.info('\n3) READ LEARNER INFORMATION --------------------------------------')
    instructor_user.legal_admin = False
    instructor_user.save()
    rest_api_client.force_authenticate(user=instructor_user)

    str_path = '/api/v2/institution/{}/learner/{}/'.format(institution_id, new_learner_id)
    str_response = 'RESPONSE Informed Consent id={}:'.format(new_learner_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Learner Information', str_response, 200)

    # TODO? Read Learner information errors

    # 4) Update learner
    """ ---------------------------------------------------------------------
    UPDATE LEARNER:
        PUT /api/v2/institution/(int: institution_id)/learner/(int: learner_id)¶
        Status Codes:
            200 OK – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
            404 Not Found – Learner not found
    Request Headers: Authorization - JWT with Institution Admin privileges
    """
    logging.info('\n4) UPDATE LEARNER --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_data = {'uid': 'LEARNER_UID_UPDATED', 'email': 'mail_test_UPDATED@tesla-ce.eu',
                'first_name': 'TEST_LEARNER_NAME_UPDATED',
                'last_name': 'TEST_LEARNER_LASTNAME_UDPATED'}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Update Learner', 'RESPONSE: ', 200)

    # TODO? Update Learner errors

    # 5) Delete learner
    """ ---------------------------------------------------------------------
    DELETE LEARNER:
        DELETE /api/v2/institution/(int: institution_id)/learner/(int: learner_id)
        Status Codes:
            200 OK – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
            404 Not Found – Learner not found
    Request Headers: Authorization - JWT with Institution Admin/Legal privileges
    """
    logging.info('\n5) DELETE LEARNER --------------------------------------')

    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete Learner', "RESPONSE: ", 204)

    # Ensure number of learners has decreased
    str_path = '/api/v2/institution/{}/learner/'.format(institution_id)
    str_message = 'RESPONSE institution_id:{}'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List learners', str_message, 200)
    assert body['count'] == n_learners

    # TODO? Delete learner errors

    # pytest.skip("TODO")
