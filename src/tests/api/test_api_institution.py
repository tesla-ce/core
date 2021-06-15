#  Copyright (c) 2020 Xavier Baró
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
import logging

import pytest

import tests.utils

@pytest.mark.django_db
def getting_variables(body, institution_id) -> object:
    institution_empty = True
    id_non_existing_institution = 1000000
    n_institution = body['count']

    if n_institution > 0:
        institution_empty = False
        id_first_institution = body['results'][0]['id']
    else:
        id_first_institution = -1

    return {
            'institution_empty': institution_empty,
            'n_institution': n_institution,
            'id_first_institution': id_first_institution,
            'id_non_existing_institution': id_non_existing_institution
        }


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


@pytest.mark.django_db
def test_api_institution_informed_consent(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Read informed consent information
    # TODO Update informed consent
    # TODO Delete informed consent
    # TODO Create a new informed consent document
    # TODO Read informed consent document information
    # TODO Update informed consent document
    # TODO Delete informed consent document
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/institution/',
                                           'List institutions', 'RESPONSE:', 200)
    variables = getting_variables(body, institution_id)
    if variables['n_institution'] > 0:
        args = [['List Institutions'], ['ID FIRST INSTITUTION: ', variables['id_first_institution']],
                ['NUMBER OF INSTITUTIONS:', variables['n_institution']],
                ['INSTITUTION ID TEST', institution_id],
                ['ID NON EXISTING INSTITUTION:', variables['id_non_existing_institution']]]
    else:
        args = [['List Institutions'], ['Empty Institutions list. Reading first Institution test will be skipped.']]

    tests.utils.print_log(args)

    logging.info('\nTESTING INSTITUTIONS: Informed consents *********************************************')
    """ ---------------------------------------------------------------------
     LIST INFORMED CONSENTS:
        GET /api/v2/institution/(int:institution_id)/ic/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found

     Privileges: Institution privileges
     """
    logging.info('\n4) LIST INFORMED CONSENTS --------------------------------------')
    if not variables['institution_empty']:
        str_url = '/api/v2/institution/' + str(institution_id) + '/ic/'
        str_response = 'RESPONSE id=' + str(institution_id) + ':'
        tests.utils.get_rest_api_client(rest_api_client,
                                        str_url,
                                        'List Informed Consents', str_response, 200)

        """ ---------------------------------------------------------------------
         CREATE A NEW INFORMED CONSENT:
            POST /api/v2/institution/(int:institution_id)/ic/
            Status Codes:
                201 Created – Created
                400 Bad Request – Invalid information provided. The response contains the description of the errors.
                404 Not Found – Institution not found

         Privileges: Institution Legal privileges
         """
        institution_user.legal_admin = True
        institution_user.save()
        rest_api_client.force_authenticate(user=institution_user)

        # Version format: X.Y.Z (with X, Y and Z integer values
        # Date format: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].']
        str_data = {'version': '0.0.2', 'valid_from': '2021-06-01T10:00'}
        tests.utils.post_rest_api_client(rest_api_client, str_url,
                                         str_data, 'Create a new Informed Consent', 'RESPONSE:', 201)
        str_data_bad_request = {'version': '1'}
        tests.utils.post_rest_api_client(rest_api_client, str_url,
                                         str_data_bad_request, 'Create a new Informed Consent', 'RESPONSE:', 400)

        # 666 403: if institution does not exist, the current user is not allowed
        # 666 should return 404?
        # str_url_not_found = '/api/v2/institution/' + str(id_non_existing_institution) + '/ic/'
        # tests.utils.post_rest_api_client(rest_api_client, str_url_not_found,
        #                                  str_data, 'Create a new Informed Consent', 'RESPONSE:', 403)

# 666 REMOVE NEXT BAKCUP FUNCTION WHEN TEST_API_INSTITUTION_INFORMED_CONSENT WILL WORK PROPERLY
def backup_test_api_institution_informed_consent(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Create a new informed consent
    # TODO Read informed consent information
    # TODO Update informed consent
    # TODO Delete informed consent
    # TODO List informed consent documents
    # TODO Create a new informed consent document
    # TODO Read informed consent document information
    # TODO Update informed consent document
    # TODO Delete informed consent document
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    body = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/institution/',
                                           'List institutions', 'RESPONSE:', 200)

    institution_empty = True
    id_non_existing_institution = 1000000
    n_institution = body['count']
    if n_institution > 0:
        institution_empty = False
        id_first_institution = body['results'][0]['id']
        # pagination test
        tests.utils.check_pagination(rest_api_client, body)

        args = [['List Institutions'], ['ID FIRST INSTITUTION: ', id_first_institution],
                ['NUMBER OF INSTITUTIONS:', n_institution],
                ['INSTITUTION ID TEST', institution_id],
                ['ID NON EXISTING INSTITUTION:', id_non_existing_institution]]
    else:
        id_first_institution = -1
        args = [['List Institutions'], ['Empty Institutions list. Reading first Institution test will be skipped.']]

    tests.utils.print_log(args)

    logging.info('\nTESTING INSTITUTIONS: Informed consents *********************************************')
    # TODO Informed Consent
    """ ---------------------------------------------------------------------
     LIST INFORMED CONSENTS:
        GET /api/v2/institution/(int:institution_id)/ic/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found

     Privileges: Institution privileges
     """
    logging.info('\n4) LIST INFORMED CONSENTS --------------------------------------')
    if not institution_empty:
        str_url = '/api/v2/institution/' + str(institution_id) + '/ic/'
        str_response = 'RESPONSE id=' + str(institution_id) + ':'
        tests.utils.get_rest_api_client(rest_api_client,
                                        str_url,
                                        'List Informed Consents', str_response, 200)

        """ ---------------------------------------------------------------------
         CREATE A NEW INFORMED CONSENT:
            POST /api/v2/institution/(int:institution_id)/ic/
            Status Codes:
                201 Created – Created
                400 Bad Request – Invalid information provided. The response contains the description of the errors.
                404 Not Found – Institution not found

         Privileges: Institution Legal privileges
         """
        institution_user.legal_admin = True
        institution_user.save()
        rest_api_client.force_authenticate(user=institution_user)

        # Version format: X.Y.Z (with X, Y and Z integer values
        # Date format: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].']
        str_data = {'version': '0.0.2', 'valid_from': '2021-06-01T10:00'}
        tests.utils.post_rest_api_client(rest_api_client, str_url,
                                         str_data, 'Create a new Informed Consent', 'RESPONSE:', 201)
        str_data_bad_request = {'version': '1'}
        tests.utils.post_rest_api_client(rest_api_client, str_url,
                                         str_data_bad_request, 'Create a new Informed Consent', 'RESPONSE:', 400)

        # 666 403: if institution does not exist, the current user is not allowed
        # 666 should return 404?
        # str_url_not_found = '/api/v2/institution/' + str(id_non_existing_institution) + '/ic/'
        # tests.utils.post_rest_api_client(rest_api_client, str_url_not_found,
        #                                  str_data, 'Create a new Informed Consent', 'RESPONSE:', 403)


@pytest.mark.django_db
def test_api_institution_course_groups(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Course Groups
    institution_user = institution_course_test_case['user'].institutionuser
    institution_id = institution_course_test_case['institution'].id
    intitution_course = institution_course_test_case['course']

    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    # Institution Admin privileges
    institution_user.inst_admin = True
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)
    # TODO List Groups
    """ ---------------------------------------------------------------------
     LIST GROUPS:
        GET /api/v2/institution/(int: institution_id)/group/
        Status Codes:
            200 OK – Ok
            404 Not Found – Institution not found
    Request Headers: Authorization - JWT with Institution Admin privileges
     """
    logging.info('\n1) LIST GROUPS --------------------------------------')
    # 666 TODO: find and add group ID instead of '/1'
    str_url = '/api/v2/institution/' + str(institution_id) + '/1/'
    str_response = 'RESPONSE id=' + str(institution_id) + ':'
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
    # 666 TODO list groups error (status 404?)


    # TODO Create a new Group
    # TODO Read group information
    # TODO Update group
    # TODO Delete group
    # TODO List courses in a group
    # TODO Add a course to a group
    # TODO Delete a course from a group
    pass


def test_api_institution_users(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Institution Users
    # TODO --> TO BE DONE!
    pass


def test_api_institution_learners(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Learners
    # TODO List learners
    # TODO Create a new Learner
    # TODO Read learner information
    # TODO Update learner
    # TODO Delete learner
    # TODO Accept an Informed Consent for a learner
    # TODO Reject current Informed Consent of a learner

    # TODO Add SEND category to a learner
    # TODO Read SEND categories assigned to a learner
    # TODO Remove a SEND Category from a learner

    pass


def test_api_institution_send(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO SEND
    # TODO List SEND Categories
    # TODO Create a new SEND Category
    # TODO Read SEND Category information
    # TODO Update SEND Category
    # TODO Delete SEND Category
    pass


def test_api_institution_instructors(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO Instructors
    # TODO --> TO BE DONE!
    pass


def test_api_institution_vle(rest_api_client, user_global_admin, institution_course_test_case):
    # TODO VLE
    # TODO List VLEs
    # TODO Create a new VLE
    # TODO Read VLE information
    # TODO Update VLE information
    # TODO Delete a VLE
    pass

# TODO INSTITUTION




#
