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


#      INSTITUTION TEST
@pytest.mark.django_db
def test_api_institution(rest_api_client, user_global_admin, institution_course_test_case):
    institution_user = institution_course_test_case['user'].institutionuser
    institution_user.inst_admin = True
    institution_user.save()

    # Check that unauthenticated calls are not allowed
    user_global_admin.is_staff = False
    user_global_admin.save()
    # TODO: add list of not allowed users as 3rd parameter to check_403 function
    tests.utils.check_403(rest_api_client, '/api/v2/institution/', [user_global_admin])

    # 666 TODO: add allowed user for testing institution. Currently admin user.
    # 666 Authorization – JWT with Global Administration privileges
    user_global_admin.is_staff = True
    user_global_admin.save()

    # Set global admin user.
    rest_api_client.force_authenticate(user=user_global_admin)

    logging.info('\nTESTING INSTITUTIONS *********************************************')

    # Get the list of Institutions
    """ ---------------------------------------------------------------------
    LIST INSTITUTIONS:
       GET /api/v2/instrument/
       Status Codes:
           200 OK – Ok
    """
    logging.info('\n1) LIST INSTITUTIONS --------------------------------------')
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
                ['ID NON EXISTING INSTITUTION:', id_non_existing_institution]]
    else:
        id_first_institution = -1
        args = [['List Institutions'], ['Empty Institutions list. Reading first Institution test will be skipped.']]

    tests.utils.print_log(args)

    # Read 1st institution information
    logging.info('\n2) READ 1st INSTITUTION INFORMATION --------------------------------------')
    # 666 TODO: READ institutions to DOC

    if not institution_empty:
        str_response = 'RESPONSE id=' + str(id_first_institution) + ':'
        tests.utils.get_rest_api_client(rest_api_client,
                                        '/api/v2/institution/' + str(id_first_institution) + '/',
                                        'Read Institution Information', str_response, 200)

    # READ non existing instrument with numeric id
    str_url = '/api/v2/institution/' + str(id_non_existing_institution) + '/'
    str_response = 'RESPONSE id=' + str(id_non_existing_institution) + ':'
    tests.utils.get_rest_api_client(rest_api_client, str_url,
                                    'Read Institution Information', str_response, 404)

    # TODO Change institution properties

# TODO INSTITUTION
# TODO Informed Consent
# TODO List informed consents
# TODO Create a new informed consent
# TODO Read informed consent information
# TODO Update informed consent
# TODO Delete informed consent
# TODO List informed consent documents
# TODO Create a new informed consent document
# TODO Read informed consent document information
# TODO Update informed consent document
# TODO Delete informed consent document
# TODO Course Groups
# TODO List Groups
# TODO Create a new Group
# TODO Read group information
# TODO Update group
# TODO Delete group
# TODO List courses in a group
# TODO Add a course to a group
# TODO Delete a course from a group
# TODO SEND
# TODO List SEND Categories
# TODO Create a new SEND Category
# TODO Read SEND Category information
# TODO Update SEND Category
# TODO Delete SEND Category
# TODO Institution Users
# TODO --> TO BE DONE!
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
# TODO Instructors
# TODO --> TO BE DONE!
# TODO VLE
# TODO List VLEs
# TODO Create a new VLE
# TODO Read VLE information
# TODO Update VLE information
# TODO Delete a VLE
