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
""" Test module for institution course learners management """
import pytest

import tests.utils


@pytest.mark.django_db
def test_api_institution_course_learners(rest_api_client, user_global_admin, institution_course_test_case):
    # institution
    institution_id = institution_course_test_case['institution'].id
    # institution user
    institution_user = institution_course_test_case['user'].institutionuser
    institution_user_uid = institution_user.uid
    # instructor
    instructor = institution_course_test_case['instructor']
    instructor_user = instructor.institutionuser
    instructor_user_id = instructor_user.id
    # learner
    learner = institution_course_test_case['learner']
    learner_user = learner.institutionuser
    learner_user_id = learner_user.id

    pytest.skip('TODO')

    # Get the list of courses for a normal Institution User not belonging to any course
    institution_user.inst_admin = False
    institution_user.data_admin = False
    institution_user.save()
    rest_api_client.force_authenticate(user=institution_user)
    courses_url = '/api/v2/institution/{}/course/'.format(institution_id)
    inst_admin_resp = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                      'List Courses Inst User', 'RESPONSE:', 200)
    assert inst_admin_resp['count'] == 0

    # Get the list of courses for a learner user and select her course_id
    rest_api_client.force_authenticate(user=learner_user)
    str_module = 'List of Learner\'s Courses (Learner user privileges)'
    str_message_learner = 'RESPONSE institution_id:{} learner_user_id:{}'.format(institution_id, learner_user_id)
    courses_list = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                   str_module, str_message_learner, 200)
    n_courses = courses_list['count']
    assert n_courses == 1
    # Select first course
    course_id = courses_list['results'][0]['id']

    # An Instructor user adds a learner to course.
    rest_api_client.force_authenticate(user=instructor_user)
    str_path_learner = '{}{}/learner/'.format(courses_url, course_id)
    str_data = {'uid': institution_user.uid}
    tests.utils.post_rest_api_client(rest_api_client, str_path_learner, str_data,
                                     'Add new instructor to a course', 'RESPONSE: ', 201)
    str_module = 'List learners from a course (Instructor user privileges)'
    str_message_instructor = 'RESPONSE institution_id:{} course_id:{} instructor_user_id:{}'.format(institution_id,
                                                                                                    course_id,
                                                                                                    instructor_user_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_learner,
                                           str_module, str_message_instructor, 200)
    n_learners = body['count']
    assert n_learners == 2

    # Learner cannot add/delete new learner to a course
    rest_api_client.force_authenticate(user=learner_user)
    str_data = {'uid': institution_user_uid}
    tests.utils.post_rest_api_client(rest_api_client, str_path_learner, str_data,
                                     'Add new learner to a course (Learner user privilege)',
                                     'RESPONSE: ', 403)

    # Learner can read only her own information: List learners from a course (learner user privileges)
    str_module = 'List learners from a course (Learner user privileges)'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_learner,
                                           str_module, str_message_learner, 200)
    assert body['count'] == 1
    assert body['results'][0]['id'] == learner_user_id

    # An instructor user adds an instructor to course.
    rest_api_client.force_authenticate(user=instructor_user)
    str_path_instructor = '{}{}/instructor/'.format(courses_url, course_id)
    str_data = {'uid': institution_user.uid}
    tests.utils.post_rest_api_client(rest_api_client, str_path_instructor, str_data,
                                     'Add new instructor to a course', 'RESPONSE: ', 201)
    str_module = 'List instructor from a course (Instructor user privileges)'
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_instructor,
                                           str_module, str_message_instructor, 200)
    n_instructors = body['count']
    assert n_instructors == 2

    # Learner cannot add/delete new instructor to a course
    rest_api_client.force_authenticate(user=learner_user)
    tests.utils.post_rest_api_client(rest_api_client, str_path_instructor, str_data,
                                     'Add new learner to a course (Learner user privilege)',
                                     'RESPONSE: ', 403)

    # Learner can read only her own information: List instructors from a course (learner user privileges)
    str_module = 'List of Course\'s Instructors (Learner user privileges)'
    instructors_list = tests.utils.get_rest_api_client(rest_api_client, str_path_instructor,
                                                       str_module, str_message_learner, 200)
    assert n_instructors == instructors_list['count']

    # TODO Delete learner: remove from course but not from system (institution admin)
    # 666 TODO? remove second test learner from the course?
