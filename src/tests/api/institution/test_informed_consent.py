#  Copyright (c) 2020 Mireia Bellot
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
""" Tests for institution informed consent administration """
import logging

import pytest

import tests.utils


@pytest.mark.django_db
def test_api_institution_informed_consent(rest_api_client, user_global_admin, institution_course_test_case):
    institution_user = institution_course_test_case['user'].institutionuser
    institution = institution_course_test_case['institution']
    institution_id = institution.id

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    # Institution privileges
    institution_user.inst_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    logging.info('\nTESTING INSTITUTIONS: Informed consents *********************************************')
    """ ---------------------------------------------------------------------
     LIST INFORMED CONSENTS:
        GET /api/v2/institution/(int:institution_id)/ic/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
  
     Privileges: Institution privileges
     """
    logging.info('\n1) LIST INFORMED CONSENTS --------------------------------------')
    str_path = '/api/v2/institution/{}/ic/'.format(institution_id)
    str_response = 'RESPONSE institution_id={}:'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Informed Consents', str_response, 200)
    # Ensure that no informed consent exists
    assert body['count'] == 0

    # Create a new informed consent
    """ ---------------------------------------------------------------------
    CREATE A NEW INFORMED CONSENT:
    POST /api/v2/institution/(int:institution_id)/ic/
    Status Codes:
        201 Created – Created
        400 Bad Request – Invalid information provided. The response contains the description of the errors.
        404 Not Found – Institution not found

    Privileges: Institution Legal privileges
    """
    logging.info('\n2) CREATE A NEW INFORMED CONSENT --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    # Version format: X.Y.Z (with X, Y and Z integer values
    # Date format: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].']
    str_data = {'version': '0.0.2', 'valid_from': '2021-06-01T10:00'}
    new_ic_id = tests.utils.post_rest_api_client(rest_api_client, str_path,
                                                 str_data, 'Create a new Informed Consent',
                                                 'RESPONSE:', 201)

    # List Informed Consents
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Informed Consents', str_response, 200)
    # Ensure Informed Consent exists
    n_ic = body['count']
    assert n_ic > 0

    # Status 400: Bad request
    str_data_bad_request = {'version': '1'}
    tests.utils.post_rest_api_client(rest_api_client, str_path,
                                     str_data_bad_request, 'Create a new Informed Consent',
                                     'RESPONSE:', 400)

    # TODO? Read Informed Consent information errors: status 404

    # Create a new informed consent
    """ ---------------------------------------------------------------------
    READ INFORMED CONSENT INFORMATION:
    GET /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/
    Status Codes:
        200 OK – Ok
        404 Not Found – Institution not found
        404 Not Found – Informed consent not found

    Privileges: Institution privileges
    """
    logging.info('\n3) READ INFORMED CONSENT INFORMATION --------------------------------------')
    institution_user.legal_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/ic/{}/'.format(institution_id, new_ic_id)
    str_response = 'RESPONSE Informed Consent id={}:'.format(new_ic_id)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Informed Consent Information', str_response, 200)

    # TODO? Read Informed Consent information errors: status 404 institution and/or informed consent not found

    # Update informed consent
    """ ---------------------------------------------------------------------
    UPDATE INFORMED CONSENT:
        PUT /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/
        Status Codes:
            200 OK – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
            404 Not Found – Informed consent not found
    Request Headers: Authorization - JWT with Institution Legal privileges
    """
    logging.info('\n4) UPDATE INFORMED CONSENT --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_data = {'version': '0.1.666', 'valid_from': '2021-06-06T23:00:00Z'}
    tests.utils.put_rest_api_client(rest_api_client, str_path, str_data,
                                    'Update Informed Consent', 'RESPONSE: ', 200)

    # TODO? Update Informed Consent errors: status 400 & 404

    # List informed consent documents
    """ ---------------------------------------------------------------------
    LIST INFORMED CONSENT DOCUMENTS:
        GET /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/document/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Informed consent not found
            404 Not Found – Informed consent document not found
    Request Headers: Authorization - JWT with Institution privileges
    """
    logging.info('\n5) LIST INFORMED CONSENT DOCUMENTS--------------------------------------')
    institution_user.legal_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/ic/{}/document/'.format(institution_id, new_ic_id)
    str_response = 'RESPONSE institution_id={}, informed consent id={}:'.format(institution_id, new_ic_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Informed Consent Documents', str_response, 200)
    # Ensure that no informed consent document exists
    assert body['count'] == 0

    # Create a new informed consent document
    """ ---------------------------------------------------------------------
    CREATE A NEW INFORMED CONSENT DOCUMENT:
    The document for each language is provided by HTML and with an attached file. .. 
    http:post:: /api/v2/institution/(int:institution_id)/ic/(int:consent_id)/document/
        Status Codes:
            201 Created – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            400 Not Found – Institution not found
            404 Not Found – Informed consent not found
    Request Headers: Authorization - JWT with Institution Legal privileges
    """
    logging.info('\n6) CREATE A NEW INFORMED CONSENT DOCUMENT --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    # 666 TODO HOW TO ADD THE ATTACHED FILE AS THE NEW INFORMED CONSENT DOCUMENT?
    # str_data = {'version': '0.0.2', 'valid_from': '2021-06-01T10:00'}
    language = 'en'
    str_data = {'language': language}
    new_ic_document_id = tests.utils.post_rest_api_client(rest_api_client, str_path,
                                                          str_data, 'Create a new Informed Consent Document',
                                                          'RESPONSE:', 201)

    # aux = 'new_ic_document_id:{}'.format(new_ic_document_id)
    # tests.utils.print_log(aux)
    # List Informed Consents
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Informed Consents', str_response, 200)
    # Ensure Informed Consent exists
    n_ic_document = body['count']
    assert n_ic_document > 0

    # Read informed consent document information
    """ ---------------------------------------------------------------------
    READ INFORMED CONSENT DOCUMENT INFORMATION:
        GET /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/document/(str: language)/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Informed consent not found
            404 Not Found – Informed consent document not found
    Request Headers: Authorization - JWT with Institution privileges
    """
    logging.info('\n7) READ INFORMED CONSENT DOCUMENT INFORMATION --------------------------------------')
    institution_user.legal_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    # language = 'en'
    str_path = '/api/v2/institution/{}/ic/{}/document/{}/'.format(institution_id, new_ic_id, language)
    str_response = 'RESPONSE Informed Consent id={}, language={}:'.format(new_ic_id, language)
    tests.utils.get_rest_api_client(rest_api_client, str_path,
                                    'Read Informed Consent Document Information',
                                    str_response, 200)

    # TODO Update informed consent document
    """ ---------------------------------------------------------------------
    UPDATE INFORMED CONSENT DOCUMENT:
        PUT /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/document/(str: language)/
        Status Codes:
            200 OK – Ok
            400 Bad Request – Invalid information provided. The response contains the description of the errors.
            404 Not Found – Institution not found
            404 Not Found – Informed consent not found
            404 Not Found – Informed consent document not found
    Request Headers: Authorization - JWT with Institution Legal privileges
    """
    logging.info('\n8) UPDATE INFORMED CONSENT DOCUMENT --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)
    # 666 TODO how to update an informed consent document? adding a new attached file??

    # TODO Read informed consent document information

    # Delete informed consent document
    """ ---------------------------------------------------------------------
    DELETE INFORMED CONSENT DOCUMENT:
        DELETE /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/document/(str: language)/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Informed consent not found
            404 Not Found – Informed consent document not found
    Request Headers: Authorization - JWT with Institution Legal privileges
    """
    logging.info('\n9) DELETE INFORMED CONSENT DOCUMENT --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/ic/{}/document/{}/'.format(institution_id, new_ic_id, language)
    # 666 check source https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.7
    # A successful response SHOULD be 200 (OK) if the response includes an entity describing the status,
    # 202 (Accepted) if the action has not yet been enacted, or 204 (No Content) if the action has been enacted
    # but the response does not include an entity.
    # 666 ADD THOSE STATUS TO DOC?
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete Informed Consent Document', "RESPONSE: ", 204)

    # List Informed Consents
    str_path = '/api/v2/institution/{}/ic/{}/document/'.format(institution_id, new_ic_id)
    str_response = 'RESPONSE institution_id={}, informed consent id={}:'.format(institution_id, new_ic_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Informed Consent Documents', str_response, 200)
    logging.info(body)
    # Ensure number of Informed Consent Documents has decreased
    assert body['count'] == (n_ic_document - 1)

    # Delete informed consent
    """ ---------------------------------------------------------------------
    DELETE INFORMED CONSENT:
        DELETE /api/v2/institution/(int: institution_id)/ic/(int: consent_id)/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
            404 Not Found – Informed consent not found
    Request Headers: Authorization - JWT with Institution Legal privileges
    """
    logging.info('\n10) DELETE INFORMED CONSENT --------------------------------------')
    institution_user.legal_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)

    str_path = '/api/v2/institution/{}/ic/{}/'.format(institution_id, new_ic_id)
    # 666 check source https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.7
    # A successful response SHOULD be 200 (OK) if the response includes an entity describing the status,
    # 202 (Accepted) if the action has not yet been enacted, or 204 (No Content) if the action has been enacted
    # but the response does not include an entity.
    # 666 ADD THOSE STATUS TO DOC?
    tests.utils.delete_rest_api_client(rest_api_client, str_path,
                                       'Delete Informed Consent', "RESPONSE: ", 204)

    # List Informed Consents
    str_path = '/api/v2/institution/{}/ic/'.format(institution_id)
    str_response = 'RESPONSE institution_id={}:'.format(institution_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           'List Informed Consents', str_response, 200)
    logging.info(body)
    # Ensure number of Informed Consent has decreased
    assert body['count'] == (n_ic - 1)
