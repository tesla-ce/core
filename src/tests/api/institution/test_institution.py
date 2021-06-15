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
def test_api_institution_institution(rest_api_client, user_global_admin, institution_course_test_case):
    """

    INSTITUTION TEST: INSTITUTION
       1) List institutions
       2) Read institution information
       3) Change institution properties
    """
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id

    # Check that unauthenticated calls are not allowed
    user_global_admin.is_staff = False
    user_global_admin.save()
    # TODO: add list of not allowed users as 3rd parameter to check_403 function
    tests.utils.check_403(rest_api_client, '/api/v2/institution/', [user_global_admin])

    # 666 Authorization – JWT with Global Administration privileges
    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    logging.info('\nTESTING INSTITUTIONS: Institutions *********************************************')

    # Get the list of Institutions
    """ ---------------------------------------------------------------------
    LIST INSTITUTIONS:
       GET /api/v2/institution/
       Status Codes:
           200 OK – Ok
    Request Headers: Authorization - JWT with Global Administration privileges
    """
    logging.info('\n1) LIST INSTITUTIONS --------------------------------------')
    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/institution/',
                                           'List institutions', 'RESPONSE:', 200)
    variables = getting_variables(body, institution_id)
    if variables['n_institution'] > 0:
        tests.utils.check_pagination(rest_api_client, body)
        args = [['List Institutions'], ['ID FIRST INSTITUTION: ', variables['id_first_institution']],
                ['NUMBER OF INSTITUTIONS:', variables['n_institution']],
                ['INSTITUTION ID TEST', institution_id],
                ['ID NON EXISTING INSTITUTION:', variables['id_non_existing_institution']]]
    else:
        args = [['List Institutions'], ['Empty Institutions list. Reading first Institution test will be skipped.']]

    tests.utils.print_log(args)


    """ ---------------------------------------------------------------------
    READ INSTITUTION INFORMATION:
       GET /api/v2/institution/(int:institution_id)/
       Status Codes:
           200 OK – Ok
           404 Not Found - Institution not found

    Request Headers: Authorization - JWT with Institution privileges
    """
    # Read 1st institution information
    logging.info('\n2) READ 1st INSTITUTION INFORMATION --------------------------------------')
    # 666 TODO: READ institutions to DOC
    rest_api_client.force_authenticate(user=institution_user)

    if not variables['institution_empty']:
        str_url = '/api/v2/institution/' + str(institution_id) + '/'
        str_response = 'RESPONSE id=' + str(institution_id) + ':'
        tests.utils.get_rest_api_client(rest_api_client,
                                        str_url,
                                        'Read Institution Information', str_response, 200)

    # TODO? READ non existing instrument with numeric id - Status 404

    """ ---------------------------------------------------------------------
    CHANGE INSTITUTION PROPERTIES:
       PUT /api/v2/institution/(int:institution_id)/
       Status Codes:
           200 OK – Ok
           400 Bad Request - Invalid information provided. The response contains the description of the errors.
           404 Not Found – Institution not found

    Request Headers: Authorization - JWT with Institution Administration privileges
    """
    # [Status: 200] UPDATE (Change) institution properties
    logging.info('\n3) CHANGE INSTITUTION PROPERTIES --------------------------------------')

    # Privileges: Institution Admin
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    # 666     if not institution_empty:
    str_data = {'acronym': 'CHANGED', 'name': 'CHANGED_NAME', 'external_ic': True,
                'mail_domain': 'CHANGED_MAIL_DOMAIN.COM', "disable_vle_learner_creation": True,
                'disable_vle_instructor_creation': True, 'disable_vle_user_creation': True}
    str_path = '/api/v2/institution/' + str(institution_id) + '/'
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Change Institution Properties', 'RESPONSE:', 200)

    # [Status: 400] Invalid information provided. The response contains the description of the errors.
    str_data = {'external_ic': 23}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Change Institution Properties', 'RESPONSE:', 400)

    # TODO? [Status: 404] UPDATE NON EXISTING instrument
