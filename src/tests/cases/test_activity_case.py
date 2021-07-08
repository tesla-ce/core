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

from tesla_ce.models.learner import get_missing_enrolment


@pytest.mark.django_db(transaction=False)
def test_activity_case_complete(rest_api_client, user_global_admin):
    """
        Complete case use for TeSLA
        :param rest_api_client: API client
        :param user_global_admin: Global administrator object
    """

    #case_methods.worker_test()

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
    send_category = case_methods.api_create_send_categories(send_admin, [ks_id])

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

    # The VLE creates a launcher for the instructor
    instructor_launcher = case_methods.vle_create_launcher(vle, instructors[0])

    # An instructor configures the activity using the API
    case_methods.api_configure_activity(instructor_launcher, activity, providers)

    for learner in learners:
        # VLE check the status of the Informed Consent of the learner
        case_methods.vle_check_learner_ic(vle, course, learner, missing=True)

        # The VLE fails to create an assessment session because IC is missing
        case_methods.vle_create_assessment_session(vle, learner, activity, ic=False)

        # The VLE creates a launcher for the learner to accept IC
        launcher_ic = case_methods.vle_create_launcher(vle, learner)

        # The learner accepts the IC using the API
        case_methods.api_learner_accept_ic(launcher_ic)

        # VLE check the status of the Informed Consent of the learner
        case_methods.vle_check_learner_ic(vle, course, learner, missing=False)

        # The VLE fails to create an assessment session because of enrolment
        case_methods.vle_create_assessment_session(vle, learner, activity, ic=True, enrolment=False)

    # The SEND admin assigns send category to the learner
    case_methods.api_set_learner_send(send_admin, send_category, learners[1])

    # Invalidate cache to avoid refresh time due to send status change
    get_missing_enrolment.invalidate(learners[1]['id'], activity['id'])

    # The VLE creates a launcher for the learners to check enrolments
    launcher_enrol1 = case_methods.vle_create_launcher(vle, learners[0])
    launcher_enrol2 = case_methods.vle_create_launcher(vle, learners[1])

    # A learner check their enrolment status via API
    l1_enrolment = case_methods.api_learner_enrolment(launcher_enrol1)
    assert len(l1_enrolment) == 0
    l2_enrolment = case_methods.api_learner_enrolment(launcher_enrol2)
    assert len(l2_enrolment) == 0

    # The VLE creates a launcher for the learners to check enrolments required for activity
    launcher_act_enrol1 = case_methods.vle_create_launcher(vle, learners[0])
    launcher_act_enrol2 = case_methods.vle_create_launcher(vle, learners[1])

    # A learner check missing enrolments for an activity via API
    l1_missing_enrolment = case_methods.api_learner_missing_enrolment(launcher_act_enrol1, activity, missing=True)
    assert providers['fr']['instrument']['id'] not in l1_missing_enrolment['instruments']  # Alternative instrument
    assert providers['ks']['instrument']['id'] in l1_missing_enrolment['instruments']  # Primary instrument
    assert providers['plag']['instrument']['id'] not in l1_missing_enrolment['instruments']  # No enrolment

    l2_missing_enrolment = case_methods.api_learner_missing_enrolment(launcher_act_enrol2, activity, missing=True)
    assert providers['fr']['instrument']['id'] in l2_missing_enrolment['instruments']  # Enabled as primary is disabled
    assert providers['ks']['instrument']['id'] not in l2_missing_enrolment['instruments']  # Disabled by SEND
    assert providers['plag']['instrument']['id'] not in l2_missing_enrolment['instruments']  # No enrolment

    # The VLE checks the enrolment status for the learner (missing is expected as is new learner)
    missing1 = case_methods.vle_create_assessment_session(vle, learners[0], activity, enrolment=False)
    assert providers['fr']['instrument']['id'] not in missing1['enrolments']['instruments']  # Alternative instrument
    assert providers['ks']['instrument']['id'] in missing1['enrolments']['instruments']  # Primary instrument
    assert providers['plag']['instrument']['id'] not in missing1['enrolments']['instruments']  # No enrolment
    missing2 = case_methods.vle_create_assessment_session(vle, learners[1], activity, enrolment=False)
    assert providers['fr']['instrument']['id'] in missing2['enrolments']['instruments']  # Enabled as disabled primary
    assert providers['ks']['instrument']['id'] not in missing2['enrolments']['instruments']  # Disabled by SEND
    assert providers['plag']['instrument']['id'] not in missing2['enrolments']['instruments']  # No enrolment

    # The VLE creates a launcher for the learner to perform the enrolment
    launcher_enrol1 = case_methods.vle_create_launcher(vle, learners[0])
    launcher_enrol2 = case_methods.vle_create_launcher(vle, learners[1])

    # The learner perform enrolment for missing instruments, sending data using LAPI
    provider_validation_tasks = []
    provider_validation_tasks += case_methods.api_lapi_perform_enrolment(
        launcher_enrol1, list(missing1['enrolments']['instruments'].keys())
    )
    provider_validation_tasks += case_methods.api_lapi_perform_enrolment(
        launcher_enrol2, list(missing2['enrolments']['instruments'].keys())
    )

    # The VLE creates a launcher for the learners to check enrolments
    launcher_enrol_pre_val1 = case_methods.vle_create_launcher(vle, learners[0])
    launcher_enrol_pre_val2 = case_methods.vle_create_launcher(vle, learners[1])

    # A learner check their enrolment status via API
    l1_enrolment_pre_val = case_methods.api_learner_enrolment(launcher_enrol_pre_val1)
    assert len(l1_enrolment_pre_val) == 1
    assert l1_enrolment_pre_val[0]['instrument_id'] == providers['ks']['instrument']['id']
    assert len(l1_enrolment_pre_val[0]['not_validated']) == 1
    assert l1_enrolment_pre_val[0]['not_validated'][0]['provider_id'] == providers['ks']['id']
    assert l1_enrolment_pre_val[0]['not_validated'][0]['instrument_id'] == providers['ks']['instrument']['id']
    assert l1_enrolment_pre_val[0]['not_validated'][0]['count'] == providers['ks']['instrument']['id'] * 4
    assert len(l1_enrolment_pre_val[0]['pending']) == 0

    l2_enrolment_pre_val = case_methods.api_learner_enrolment(launcher_enrol_pre_val2)
    assert len(l2_enrolment_pre_val) == 1
    assert l2_enrolment_pre_val[0]['instrument_id'] == providers['fr']['instrument']['id']
    assert len(l2_enrolment_pre_val[0]['not_validated']) == 1
    assert l2_enrolment_pre_val[0]['not_validated'][0]['provider_id'] == providers['fr']['id']
    assert l2_enrolment_pre_val[0]['not_validated'][0]['instrument_id'] == providers['fr']['instrument']['id']
    assert l2_enrolment_pre_val[0]['not_validated'][0]['count'] == providers['fr']['instrument']['id'] * 4
    assert len(l2_enrolment_pre_val[0]['pending']) == 0

    # Providers validate samples in their queues
    validation_summary_tasks = case_methods.provider_validate_samples(providers, provider_validation_tasks)

    # The VLE creates a launcher for the learners to check enrolments
    launcher_enrol_post_val1 = case_methods.vle_create_launcher(vle, learners[0])
    launcher_enrol_post_val2 = case_methods.vle_create_launcher(vle, learners[1])

    # A learner check their enrolment status via API
    l1_enrolment_post_val = case_methods.api_learner_enrolment(launcher_enrol_post_val1)
    assert len(l1_enrolment_post_val) == 1
    assert l1_enrolment_post_val[0]['instrument_id'] == providers['ks']['instrument']['id']
    assert len(l1_enrolment_post_val[0]['not_validated']) == 0
    assert l1_enrolment_post_val[0]['not_validated_count'] == 0
    assert len(l1_enrolment_post_val[0]['pending']) == 1
    assert l1_enrolment_post_val[0]['pending'][0]['provider_id'] == providers['ks']['id']
    assert l1_enrolment_post_val[0]['pending'][0]['instrument_id'] == providers['ks']['instrument']['id']
    assert abs(1.0 - float(l1_enrolment_post_val[0]['pending'][0]['pending_contribution'])) < 0.0001

    l2_enrolment_post_val = case_methods.api_learner_enrolment(launcher_enrol_post_val2)
    assert len(l2_enrolment_post_val) == 1
    assert l2_enrolment_post_val[0]['instrument_id'] == providers['fr']['instrument']['id']
    assert len(l2_enrolment_post_val[0]['not_validated']) == 0
    assert l2_enrolment_post_val[0]['not_validated_count'] == 0
    assert len(l2_enrolment_post_val[0]['pending']) == 1
    assert l2_enrolment_post_val[0]['pending'][0]['provider_id'] == providers['fr']['id']
    assert l2_enrolment_post_val[0]['pending'][0]['instrument_id'] == providers['fr']['instrument']['id']
    assert abs(1.0 - float(l2_enrolment_post_val[0]['pending'][0]['pending_contribution'])) < 0.0001

    # Worker compute validation summary from individual validations
    enrolment_tasks = case_methods.worker_validation_summary(validation_summary_tasks)

    # Worker distribute enrolment tasks among providers
    provider_enrolment_tasks = case_methods.worker_enrol_learner(enrolment_tasks)

    # Provider perform learners enrolment
    case_methods.provider_enrol_learners(providers, provider_enrolment_tasks)

    # The VLE creates a launcher for the learners to check enrolments
    launcher_enrol_end1 = case_methods.vle_create_launcher(vle, learners[0])
    launcher_enrol_end2 = case_methods.vle_create_launcher(vle, learners[1])

    # A learner check their enrolment status via API
    l1_enrolment_end = case_methods.api_learner_enrolment(launcher_enrol_end1)
    assert len(l1_enrolment_end) == 1
    assert l1_enrolment_end[0]['instrument_id'] == providers['ks']['instrument']['id']
    assert len(l1_enrolment_end[0]['not_validated']) == 0
    # assert len(l1_enrolment_end[0]['pending']) == 0  # TODO: Issue 30
    assert abs(1.0 - float(l1_enrolment_end[0]['percentage__min'])) < 0.0001
    assert abs(1.0 - float(l1_enrolment_end[0]['percentage__max'])) < 0.0001
    assert l1_enrolment_end[0]['can_analyse__min']
    assert l1_enrolment_end[0]['can_analyse__max']
    assert l1_enrolment_end[0]['not_validated_count'] == 0

    l2_enrolment_end = case_methods.api_learner_enrolment(launcher_enrol_end2)
    assert len(l2_enrolment_end) == 1
    assert l2_enrolment_end[0]['instrument_id'] == providers['fr']['instrument']['id']
    assert len(l2_enrolment_end[0]['not_validated']) == 0
    # assert len(l2_enrolment_end[0]['pending']) == 0  # TODO: Issue 30
    assert abs(1.0 - float(l2_enrolment_end[0]['percentage__min'])) < 0.0001
    assert abs(1.0 - float(l2_enrolment_end[0]['percentage__max'])) < 0.0001
    assert l2_enrolment_end[0]['can_analyse__min']
    assert l2_enrolment_end[0]['can_analyse__max']
    assert l2_enrolment_end[0]['not_validated_count'] == 0

    # Invalidate cache to avoid refresh time
    get_missing_enrolment.invalidate(learners[0]['id'], activity['id'])
    get_missing_enrolment.invalidate(learners[1]['id'], activity['id'])

    # The VLE creates an assessment session for a learner for the activity
    vle_options = {
        'floating_menu_initial_pos': 'top-right'
    }
    assessment_session1 = case_methods.vle_create_assessment_session(vle, learners[0], activity, vle_options)
    assessment_session2 = case_methods.vle_create_assessment_session(vle, learners[1], activity)

    # The learner perform the activity, sending information from sensors using the LAPI
    provider_verification_tasks = []
    tasks, activity_doc1 = case_methods.lapi_lerner_perform_activity(assessment_session1)
    provider_verification_tasks += tasks
    tasks, activity_doc2 = case_methods.lapi_lerner_perform_activity(assessment_session2)
    provider_verification_tasks += tasks

    # VLE send the activity
    provider_verification_tasks += case_methods.vle_send_activity(vle, assessment_session1, activity_doc1)
    provider_verification_tasks += case_methods.vle_send_activity(vle, assessment_session2, activity_doc2)

    # Provider perform verification process on data collected during the activity
    reporting_tasks = case_methods.provider_verify_request(providers, provider_verification_tasks)

    # As we have deferred providers, some of the verifications are postponed via notifications.
    notification_tasks = case_methods.worker_send_notifications()
    assert len(notification_tasks) > 0

    # Providers process those notifications to generate final verification results
    reporting_tasks += case_methods.provider_process_notifications(providers, notification_tasks, 'verification')

    # Worker process verification results to create the reports
    case_methods.worker_create_reports(reporting_tasks)

    # Instructor review the results for the activity
    launcher_report = case_methods.vle_create_launcher(vle, instructors[0])
    reports = case_methods.api_instructor_report(launcher_report, activity)
    assert len(reports) == 2
    for report in reports:
        assert report['identity_level'] == 2  # OK
        assert report['content_level'] == 2  # OK
        assert report['integrity_level'] == 1  # NO INFORMATION
        if report['learner']['id'] == learners[0]['id']:
            inst_ref = 2
        else:
            inst_ref = 1
        assert len(report['detail']) == 2
        if report['detail'][0]['instrument_id'] == 5:
            assert report['detail'][0]['identity_level'] == 1
            assert report['detail'][0]['content_level'] == 2
            assert report['detail'][0]['integrity_level'] == 1
            assert report['detail'][1]['instrument_id'] == inst_ref
            assert report['detail'][1]['identity_level'] == 2
            assert report['detail'][1]['content_level'] == 1
            assert report['detail'][1]['integrity_level'] == 1
        else:
            assert report['detail'][0]['instrument_id'] == inst_ref
            assert report['detail'][0]['identity_level'] == 2
            assert report['detail'][0]['content_level'] == 1
            assert report['detail'][0]['integrity_level'] == 1
            assert report['detail'][1]['instrument_id'] == 5
            assert report['detail'][1]['identity_level'] == 1
            assert report['detail'][1]['content_level'] == 2
            assert report['detail'][1]['integrity_level'] == 1

    # VLE get the results for the activity for integration

    # Legal admin updates Informed consent status

    # Learners IC status is not valid

    # Learner accepts new IC

    # Learner IC status is valid again

    # Add a 2nd provider with deferred process for one of the used instruments


