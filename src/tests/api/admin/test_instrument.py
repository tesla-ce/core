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
""" Tests for instrument administration """
import logging

import pytest

import tests.utils


##############################################################################
#
#   ADMIN TESTING: INSTRUMENTS
#   1) List instruments --> 2) Read 1st instrument --> 3) Read non existing instrument
#   4) Create instrument --> 5) List instruments (+1) --> 6) Read instrument --> 7) failed create instrument
#   8) update instrument --> 9) read instrument --> 10) delete instrument --> 11) list (-1)
#
##############################################################################
@pytest.mark.django_db
def test_api_admin_instruments(rest_api_client, user_global_admin):
    # TODO: add list of not allowed users as 3rd parameter to check_403 function
    # Check that unauthenticated calls are not allowed
    user_global_admin.is_staff = False
    user_global_admin.save()
    tests.utils.check_403(rest_api_client, '/api/v2/admin/instrument/', [user_global_admin])

    # Authorization – JWT with Global Administration privileges
    # Set global admin user.
    user_global_admin.is_staff = True
    user_global_admin.save()
    rest_api_client.force_authenticate(user=user_global_admin)

    logging.info('\nTESTING ORGANIC ADMIN: INSTRUMENTS*********************************************')
    """ ---------------------------------------------------------------------
    LIST INSTRUMENTS:
       GET /api/v2/admin/instrument/
       Status Codes:
           200 OK – Ok
    """
    logging.info('\n1) LIST INSTRUMENTS --------------------------------------')
    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                           'List instruments', 'RESPONSE:', 200)

    """
    Getting values for testing process
        instruments_empty: boolean value. If True, reading specific instrument is skipped.
        n_instruments: number of instruments.
        id_first_instrument: ID from first Instrument.
        id_non_existing_instrument: taking into account IDs are assigned in ordered way.
    """
    instruments_empty = True
    id_non_existing_instrument = 1000000
    n_instruments = body['count']
    if n_instruments > 0:
        instruments_empty = False
        id_first_instrument = body['results'][0]['id']

        # pagination test
        tests.utils.check_pagination(rest_api_client, body)

        args = [['List instruments'], ['ID FIRST INSTRUMENT: ', id_first_instrument],
                ['NUMBER OF INSTRUMENTS:', n_instruments],
                ['ID NON EXISTING INSTRUMENT:', id_non_existing_instrument]]
    else:
        id_first_instrument = -1
        args = [['List instruments'], ['Empty instruments list. Reading first instrument test will be skipped.']]

    tests.utils.print_log(args)

    """ -----------------------------------------------------------------------------
     Read instrument information:
       GET /api/v2/admin/instrument/(int: instrument_id)/
       Status Codes:
           200 OK – Ok
           404 Not Found – Instrument not found
    -----------------------------------------------------------------------------"""
    # READ existing 1st instrument
    logging.info('\n2) READ 1st INSTRUMENT --------------------------------------')

    if not instruments_empty:
        str_response = 'RESPONSE id=' + str(id_first_instrument) + ':'
        tests.utils.get_rest_api_client(rest_api_client,
                                        '/api/v2/admin/instrument/' + str(id_first_instrument) + '/',
                                        'Read Instrument Information', str_response, 200)

    # READ non existing instrument with numeric id
    str_url = '/api/v2/admin/instrument/' + str(id_non_existing_instrument) + '/'
    str_response = 'RESPONSE id=' + str(id_non_existing_instrument) + ':'
    tests.utils.get_rest_api_client(rest_api_client, str_url,
                                    'Read Instrument Information', str_response, 404)

    """ -----------------------------------------------------------------------------
    Create a new instrument:
       POST /api/v2/admin/instrument/
       Status Codes:
           201 Created – Created
           400 Bad Request – Invalid information provided. The response contains the description of the errors.
    -----------------------------------------------------------------------------"""
    """
       Create instrument --> List instruments(+1) --> Read instrument --> 
       update instrument --> read instrument --> delete instrument --> list(-1)
       """

    # CREATE new instrument: SUCCESS
    logging.info('\n4) CREATE INSTRUMENT --------------------------------------')
    instrument = {'acronym': 'n3', 'name': 'name3', 'queue': 'tesla_test23'}
    new_instrument_id = tests.utils.post_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                                         instrument, 'Create New Instrument', 'RESPONSE:', 201)

    # 666 TODO:DOC paràmetres doc help no diu que options_schema i queue són OBLIGATORIS. Ho afegeixo???
    # 666 primers errors RETORNA RESPONSE:
    # {'options_schema': ['This field is required.'], 'queue': ['This field is required.']}

    # LIST instruments and check count has increased.
    logging.info('\n5) LIST INSTRUMENT --------------------------------------')
    aux_body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                               'Create New Instrument', 'RESPONSE:', 200)
    # Get number of instruments
    aux_n_instruments = aux_body['count']
    str_log = [['Create New Instrument'], ['Number of Instruments PRE:', n_instruments, 'and POST:', aux_n_instruments]]
    tests.utils.print_log(str_log)
    assert aux_n_instruments == n_instruments + 1

    # READ new instrument
    logging.info('\n6) READ NEW INSTRUMENT --------------------------------------')
    str_url = '/api/v2/admin/instrument/' + str(new_instrument_id) + '/'
    tests.utils.get_rest_api_client(rest_api_client, str_url,
                                    'Create New Instrument [Read Instrument Information]',
                                    'RESPONSE id=', 200)

    # CREATE new instrument: FAILED
    logging.info('\n7) FAILED CREATION NEW INSTRUMENT --------------------------------------')
    failed_instrument = {'acronym': 'n3'}
    tests.utils.post_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                     failed_instrument, 'Create New Instrument',
                                     'RESPONSE:', 400)

    """ -----------------------------------------------------------------------------
     Update instrument information:
       PUT /api/v2/admin/instrument/(int: instrument_id)/
       Status Codes:
           200 OK – Ok
           400 Bad Request – Invalid information provided. The response contains the description of the errors.
           404 Not Found – Instrument not found 
    -----------------------------------------------------------------------------"""

    # [Status: 200] UPDATE new instrument
    logging.info('\n8) UPDATE INSTRUMENT --------------------------------------')
    str_data = {'acronym': 'CHANGED', 'name': 'name3', 'queue': 'tesla_test23'}
    str_path = '/api/v2/admin/instrument/' + str(new_instrument_id) + '/'
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data, 'Update instrument information',
                                    'RESPONSE:', 200)
    # [Status: 400] UPDATE WRONG NUMBER PARAMETERS. REQUIRED: name, queue
    str_data = {'acronym': 'CHANGED'}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data, 'Update instrument information',
                                    'RESPONSE:', 400)

    # [Status: 404] UPDATE NON EXISTING instrument
    str_path = '/api/v2/admin/instrument/' + str(new_instrument_id + 1) + '/'
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data, 'Update instrument information',
                                    'RESPONSE:', 404)

    # Read updated instrument
    logging.info('\n9) READ UPDATED INSTRUMENT --------------------------------------')
    str_path = '/api/v2/admin/instrument/' + str(new_instrument_id) + '/'
    str_response = 'RESPONSE id=' + str(new_instrument_id) + ':'
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Updated Instrument', str_response, 200)
    """-----------------------------------------------------------------------------
     Delete an instrument:
       DELETE /api/v2/admin/instrument/(int: instrument_id)/
       Status Codes:
           204 No Content – No Content
           404 Not Found – Instrument not found
    -----------------------------------------------------------------------------"""
    logging.info('\n10) DELETE UPDATED INSTRUMENT --------------------------------------')
    # Delete updated instrument
    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                           'List instruments', 'RESPONSE:', 200)
    n_instruments_pre = body['count']
    if n_instruments > 0:
        id_first_instrument_pre = body['results'][0]['id']
        while body['next'] is not None:
            body = tests.utils.get_rest_api_client(rest_api_client, body['next'], 'List instruments', 'Pagination', 200)
        id_last_instrument_pre = body['results'][len(body['results']) - 1]['id']
    else:
        id_first_instrument_pre = -1
        id_last_instrument_pre = -1

    # [Status = 204] Delete existing item
    tests.utils.delete_rest_api_client(rest_api_client, str_path, 'Delete an instrument',
                                       'DELETED', 204)

    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                           'List instruments', 'RESPONSE:', 200)
    n_instruments_post = body['count']
    if n_instruments > 0:
        id_first_instrument_post = body['results'][0]['id']
        while body['next'] is not None:
            body = tests.utils.get_rest_api_client(rest_api_client, body['next'], 'List instruments', 'Pagination', 200)
        id_last_instrument_post = body['results'][len(body['results']) - 1]['id']
    else:
        id_first_instrument_post = -1
        id_last_instrument_post = -1

    str_log = [['Delete an instrument'],
               ['PRE delete: ', n_instruments_pre, 'items - ID first item:',
                id_first_instrument_pre, '- ID last item:', id_last_instrument_pre]]
    tests.utils.print_log(str_log)

    str_log = [['Delete an instrument'],
               ['POST delete:', n_instruments_post, 'items - ID first item:',
                id_first_instrument_post, '- ID last item:', id_last_instrument_post]]
    tests.utils.print_log(str_log)

    # [Status = 404] DELETE non existing item
    tests.utils.delete_rest_api_client(rest_api_client, str_path, 'Delete an instrument',
                                       'NOT DELETED', 404)

    logging.info('\n11) LIST INSTRUMENTS -----------------------------------------------')
    tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/instrument/',
                                    'List instruments', 'RESPONSE:', 200)

    # UPDATE new instrument FAILED
    # {"id": 12, "options_schema": null, "name": "name666", "acronym": "n666", "queue": "tesla_666",
    # "enabled": false, "requires_enrolment": false, "description": "testing", "identity": false,
    # "originality": false, "authorship": false, "integrity": false,
    # "created_at": "2021-03-21T08:48:13.866822Z", "updated_at": "2021-03-21T08:48:13.866896Z"}
