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
""" Tests for institution administration """
import logging

import pytest

import tests.utils


##############################################################################
#
#   ADMIN TESTING: INSTITUTIONS

#   1) List institutions --> 2) Read 1st institution --> 3) Read non existing institution
#   4) Create institution --> 5) List institutions (check +1) --> 6) Read institution --> 7) failed create institution
#   8) update institution --> 9) read institution --> 10) delete institution --> 11) list institution (check it's -1)
#
##############################################################################
@pytest.mark.django_db
def test_api_admin_institutions(rest_api_client, user_global_admin):
    # TODO: add list of not allowed users as 3rd parameter to check_403 function
    # Check that unauthenticated calls are not allowed
    user_global_admin.is_staff = False
    user_global_admin.save()
    tests.utils.check_403(rest_api_client, '/api/v2/admin/institution/', [user_global_admin])

    # Authorization – JWT with Global Administration privileges
    # Set global admin user.
    user_global_admin.is_staff = True
    user_global_admin.save()
    rest_api_client.force_authenticate(user=user_global_admin)

    # 666 TODO: list institutions to DOC
    logging.info('\n1) LIST INSTITUTIONS --------------------------------------')
    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                           'List institutions', 'RESPONSE:', 200)

    n_institution = body['count']
    institutions_empty = True
    id_non_existing_institution = 1000000
    if n_institution > 0:
        institutions_empty = False
        id_first_institution = body['results'][0]['id']
        tests.utils.check_pagination(rest_api_client, body)
        while body['next'] is not None:
            body = tests.utils.get_rest_api_client(rest_api_client, body['next'], 'List institutions', 'Pagination',
                                                   200)
        id_last_institution = body['results'][len(body['results']) - 1]['id']
    else:
        id_first_institution = -1
        id_last_institution = -1

    tests.utils.print_log([['List Institution'], ['NUMBER OF INSTITUTIONS: ', n_institution],
                           ['ID FIRST INSTITUTION: ', id_first_institution],
                           ['ID LAST INSTITUTION: ', id_last_institution],
                           ['ID NON EXISTING INSTITUTION: ', id_non_existing_institution]])

    # READ existing 1st institution
    logging.info('\n2) READ 1st INSTITUTION --------------------------------------')

    # 666 TODO: READ institutions to DOC
    if not institutions_empty:
        str_response = 'RESPONSE id=' + str(id_first_institution) + ':'
        tests.utils.get_rest_api_client(rest_api_client,
                                        '/api/v2/admin/institution/' + str(id_first_institution) + '/',
                                        'Read Institution Information', str_response, 200)

    # READ non existing institution with numeric id
    str_url = '/api/v2/admin/institution/' + str(id_non_existing_institution) + '/'
    str_response = 'RESPONSE id=' + str(id_non_existing_institution) + ':'
    tests.utils.get_rest_api_client(rest_api_client, str_url,
                                    'Read Institution Information', str_response, 404)
    # -----------------------------------------------------------------------------
    # Create a new institution:
    #   POST /api/v2/admin/institution/
    #   Status Codes:
    #       201 Created – Created
    #       400 Bad Request – Invalid information provided. The response contains the description of the errors.
    # -----------------------------------------------------------------------------
    # CREATE new institution: SUCCESS
    logging.info('\n4) CREATE INSTITUTION --------------------------------------')
    # 666 TODO: Include mandatory fields and default values to DOC for CREATE NEW INSTITUTION
    """ 666
    acronym(string) MANDATORY field.
    name(string)  MANDATORY field
    external_ic(boolean): False by default.
    mail_domain(string): None by default.
    disable_vle_learner_creation(boolean): False by default.
    disable_vle_instructor_creation(boolean): False by default.
    disable_vle_user_creation(boolean): False by default.
    """
    institution = {'acronym': 'nni', 'name': 'name_new_institution'}
    new_institution_id = tests.utils.post_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                                          institution, 'Create New Institution', 'RESPONSE:', 201)

    # 666 TODO: trobar paràmetres obligatoris i opcionals de create institution

    # LIST institution and check count has increased.
    logging.info('\n5) LIST INSTITUTIONS --------------------------------------')
    aux_body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                               'Create New Institution', 'RESPONSE:', 200)
    # Get number of institutions
    aux_n_institution = aux_body['count']

    args = [['Create New Institution'], ['Number of Institutions PRE: ', n_institution],
            ['Number of Institutions POST:', aux_n_institution]]

    tests.utils.print_log(args)

    assert aux_n_institution == n_institution + 1

    # READ new institution
    logging.info('\n6) READ NEW INSTITUTION --------------------------------------')
    str_url = '/api/v2/admin/institution/' + str(new_institution_id) + '/'
    aux_body = tests.utils.get_rest_api_client(rest_api_client, str_url,
                                               'Create New Institution [Read Institution Information]',
                                               'RESPONSE id=', 200)
    args = [['Create New Institution [Read Institution Information]'], ['RESPONSE id=: ', new_institution_id],
            ['', aux_body]]

    tests.utils.print_log(args)
    print('Create New Institution [Read Institution Information] RESPONSE id=:', new_institution_id, ' ', aux_body)

    # CREATE new institution: FAILED
    logging.info('\n7) FAILED CREATION NEW INSTITUTION --------------------------------------')
    failed_institution = {'acronym': 'n3'}
    tests.utils.post_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                     failed_institution, 'Create New Institution',
                                     'RESPONSE:', 400)

    # -----------------------------------------------------------------------------
    # Update institution information:
    #   PUT /api/v2/admin/institution/(int: institution_id)/
    #   Status Codes:
    #       200 OK – Ok
    #       400 Bad Request – Invalid information provided. The response contains the description of the errors.
    #       404 Not Found – Institution not found
    # -----------------------------------------------------------------------------
    # [Status: 200] UPDATE new institution
    logging.info('\n8) UPDATE INSTITUTION --------------------------------------')
    str_data = {'acronym': 'CHANGED', 'name': 'name3', 'queue': 'tesla_test23'}
    str_path = '/api/v2/admin/institution/' + str(new_institution_id) + '/'
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data, 'Update institution information',
                                    'RESPONSE:', 200)
    # [Status: 400] UPDATE WRONG NUMBER PARAMETERS. REQUIRED: name, queue
    str_data = {'acronym': 'CHANGED'}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data, 'Update institution information',
                                    'RESPONSE:', 400)

    # [Status: 404] UPDATE NON EXISTING institution
    str_path = '/api/v2/admin/institution/' + str(new_institution_id + 1) + '/'
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data, 'Update institution information',
                                    'RESPONSE:', 404)

    # Read updated institution
    logging.info('\n9) READ UPDATED INSTITUTION --------------------------------------')
    str_path = '/api/v2/admin/institution/' + str(new_institution_id) + '/'
    str_response = 'RESPONSE id=' + str(new_institution_id) + ':'
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Updated Institution', str_response, 200)
    """-----------------------------------------------------------------------------
     Delete an institution:
       DELETE /api/v2/admin/institution/(int: institution_id)/
       Status Codes:
           204 No Content – No Content
           404 Not Found – Institution not found
    -----------------------------------------------------------------------------"""
    logging.info('\n10) DELETE UPDATED INSTITUTION --------------------------------------')
    # Delete updated institution
    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                           'List institutions', 'RESPONSE:', 200)
    n_institution_pre = body['count']
    if n_institution_pre > 0:
        id_first_institution_pre = body['results'][0]['id']
        while body['next'] is not None:
            body = tests.utils.get_rest_api_client(rest_api_client, body['next'], 'List institutions', 'Pagination pre',
                                                   200)
        id_last_institution_pre = body['results'][len(body['results']) - 1]['id']
    else:
        id_first_institution_pre = -1
        id_last_institution_pre = -1

    # [Status = 204] Delete existing item
    tests.utils.delete_rest_api_client(rest_api_client, str_path, 'Delete an institution',
                                       'DELETED', 204)

    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                           'List institutions', 'RESPONSE:', 200)
    n_institution_post = body['count']
    if n_institution_post > 0:
        id_first_institution_post = body['results'][0]['id']
        while body['next'] is not None:
            body = tests.utils.get_rest_api_client(rest_api_client, body['next'], 'List institutions',
                                                   'Pagination post', 200)
        id_last_institution_post = body['results'][len(body['results']) - 1]['id']
    else:
        id_first_institution_post = -1
        id_last_institution_post = -1

    str_log = [['Delete an institution'], ['PRE delete: ', n_institution_pre],
               ['items - ID first item:', id_first_institution_pre],
               ['- ID last item:', id_last_institution_pre]]
    tests.utils.print_log(str_log)

    str_log = [['Delete an institution'], ['POST delete: ', n_institution_post],
               ['items - ID first item:', id_first_institution_post],
               ['- ID last item:', id_last_institution_post]]
    tests.utils.print_log(str_log)

    # [Status = 404] DELETE non existing item
    tests.utils.delete_rest_api_client(rest_api_client, str_path, 'Delete an institution',
                                       'NOT DELETED', 404)

    logging.info('\n11) LIST INSTITUTIONS -----------------------------------------------')
    tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/institution/',
                                    'List institutions', 'RESPONSE:', 200)
