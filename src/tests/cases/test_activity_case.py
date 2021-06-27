#  Copyright (c) 2021 Xavier Baró
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
""" TeSLA CE Activity use case test """
import pytest

from . import case_methods


@pytest.mark.django_db(transaction=False)
def test_activity_case_complete(rest_api_client, user_global_admin):
    """
        Complete case use for TeSLA
        :param rest_api_client: API client
        :param user_global_admin: Global administrator object
    """

    # A global administrator register the providers
    providers = case_methods.api_register_providers(user_global_admin)

    # A global administrator creates a new institution
    institution = case_methods.api_create_institution(user_global_admin)

    # A global administrator creates a new user for the institution and assign administration rights
    inst_admin = case_methods.api_create_institution_admin(user_global_admin, institution)

    # Institution administrator creates a new legal admin
    legal_admin = case_methods.api_create_institution_legal_admin(inst_admin)

    # Institution administrator creates a new SEND admin
    send_admin = case_methods.api_create_institution_send_admin(inst_admin)

    # A legal administrator of the institution creates the Informed Consent using the API
    case_methods.api_create_ic(legal_admin)

    # A SEND administrator of the institution defines the SEND categories using the API
    ks_id = providers['ks']['instrument']['id']
    send_categories = case_methods.api_create_send_categories(send_admin, [ks_id])

    # Institution enables direct learners and instructors registration by VLE
    case_methods.api_enable_direct_registration_vle(inst_admin)

    # Institution administrator register a new VLE
    vle = case_methods.api_register_vle(inst_admin)

    # The VLE creates a new course
    course = case_methods.vle_create_course(vle)

    # The VLE enrolls course learners and instructors
    instructors, learners = case_methods.vle_enrol_users(vle, course)

    # The VLE creates a new activity
    activity = case_methods.vle_create_activity(vle, course)

    pytest.skip('TODO')

    # An instructor configures the activity using the API
    case_methods.api_configure_activity(instructors[0], activity)

    for learner in learners:
        # VLE check the status of the Informed Consent of the learner
        case_methods.vle_check_learner_ic(vle, learner, missing=True)

        # The VLE creates a launcher for the learner to accept IC
        launcher_ic = case_methods.vle_create_launcher(vle, learner)

        # The leaerner accepts the IC using the API
        case_methods.api_learner_accept_ic(learners, launcher_ic)

        # VLE check the status of the Informed Consent of the learner
        case_methods.vle_check_learner_ic(vle, learner, missing=False)

    # The VLE checks the enrolment status for the learner (missing is expected as is new learner)
    missing = case_methods.vle_check_learner_enrolment(rest_api_client, vle, learners[0], activity, missing=True)

    # The VLE creates a launcher for the learner to perform the enrolment
    launcher_enrol = case_methods.vle_create_launcher(rest_api_client, vle, learners[0])

    # The learner perform enrolment for missing instruments, sending data using LAPI
    case_methods.api_lapi_perform_enrolment(rest_api_client, learners[0], launcher_enrol, missing)

    # The VLE creates an assessment session for a learner for the activity
    assessment_session = case_methods.vle_create_assessment_session(rest_api_client, vle, learners[0], activity)

    # The VLE creates a launcher for the learner and assessment session
    launcher = case_methods.vle_create_launcher(vle, learners[0], assessment_session)

    # The learner perform the activity, sending information from sensors using the LAPI
    case_methods.lapi_lerner_perform_activity(rest_api_client, learners[0], launcher, assessment_session)

    # Instructor review the results for the activity
    case_methods.api_instructor_report(rest_api_client, instructors[0], activity)

    # VLE get the results for the activity for integration

    # Legal admin updates Informed consent status

    # Learners IC status is not valid

    # Learner accepts new IC

    # Learner IC status is valid again

    # Add SEND to one of the learners

