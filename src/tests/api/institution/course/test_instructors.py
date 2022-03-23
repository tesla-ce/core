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
""" Test module for institution course instructors management """
import logging

import pytest

import tests.utils


@pytest.mark.django_db
def test_api_institution_course_instructors(rest_api_client, user_global_admin, institution_course_test_case):
    # institution
    institution_id = institution_course_test_case['institution'].id
    # institution user
    institution_user = institution_course_test_case['user'].institutionuser
    # instructor
    instructor = institution_course_test_case['instructor']
    instructor_user = instructor.institutionuser
    instructor_user_id = instructor_user.id
    # learner
    learner = institution_course_test_case['learner']
    learner_user = learner.institutionuser
    learner_user_id = learner_user.id

    pytest.skip('TODO')

    # Get the list of courses for an instructor
    rest_api_client.force_authenticate(user=instructor_user)
    courses_url = '/api/v2/institution/{}/course/'.format(institution_id)
    str_module = 'List of Instructor\'s Courses (Instructor user privileges)'
    str_message = 'RESPONSE institution_id:{} instructor_user_id:{}'.format(institution_id, instructor_user_id)
    courses_list = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                   str_module, str_message, 200)
    n_courses = courses_list['count']
    assert n_courses == 1

    # Select first course
    course_id = courses_list['results'][0]['id']
    logging.info(course_id)
    # 666 TODO: add to code "id" vs "vle.id" vs "vle_course_id" vs "code"?!!

    # List learners from a course
    str_path_learner = '{}{}/learner/'.format(courses_url, course_id)
    str_module = 'List learners from a course (instructor user privileges)'
    str_message = 'RESPONSE institution_id:{} course_id:{} instructor_user_id:{}'.format(institution_id,
                                                                                         course_id,
                                                                                         instructor_user_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_learner,
                                           str_module, str_message, 200)
    # number of learners
    n_learners = body['count']

    # TODO Add a Learner to a Course (from instructor privileges)
    # 666 STATUS 500 + KeyError('parent_lookup_institution_id')
    ''''''
    str_data = {'uid': institution_user.uid}
    new_learner_id = tests.utils.post_rest_api_client(rest_api_client, str_path_learner, str_data,
                                                      'Add new learner to a course', 'RESPONSE: ', 201)

    # Ensure number of learners has increased
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_learner,
                                           'List learners from a course', 'RESPONSE:', 200)
    assert n_learners + 1 == body['count']
    ''''''

    # Check learner user can only list herself
    rest_api_client.force_authenticate(user=learner_user)
    # str_path = '/api/v2/institution/{}/course/{}/learner/'.format(institution_id, course_id)
    str_module = 'List learners from a course (learner user privileges)'
    str_message = 'RESPONSE institution_id:{} course_id:{} learner_user_id:{}'.format(institution_id,
                                                                                      course_id,
                                                                                      learner_user_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_learner,
                                           str_module, str_message, 200)
    assert body['count'] == 1
    assert body['results'][0]['id'] == learner_user_id

    rest_api_client.force_authenticate(user=instructor_user)

    # TODO Remove a Learner from a Course but not from system (from instructor)
    '''
    # str_path = '/api/v2/institution/{}/course/{}/learner/{}/'.format(institution_id, course_id, new_learner_id)
    tests.utils.delete_rest_api_client(rest_api_client, str_path_learner,
                                       'Delete Learner from a Course', "RESPONSE: ", 204)
    assert body['count'] == n_learners
    
    # 666 TODO: check user still exist in the system?
    
    '''
    # List instructors from a course
    rest_api_client.force_authenticate(user=instructor_user)
    str_path_instructor = '{}{}/instructor/'.format(courses_url, course_id)
    str_module = 'List of Course\'s Instructors (Instructor user privileges)'
    str_message = 'RESPONSE institution_id:{} course_id:{} instructor_user_id:{}'.format(institution_id,
                                                                                         course_id,
                                                                                         instructor_user_id)
    instructors_list = tests.utils.get_rest_api_client(rest_api_client, str_path_instructor,
                                                       str_module, str_message, 200)
    n_instructors = instructors_list['count']
    assert n_instructors == 1
    assert instructors_list['results'][0]['id'] == instructor_user_id

    # TODO Add existing user as a instructor to a course (from instructor privileges)
    ''''''
    str_data = {'uid': institution_user.uid}
    new_instructor_id = tests.utils.post_rest_api_client(rest_api_client, str_path_instructor, str_data,
                                                         'Add new instructor to a course', 'RESPONSE: ', 201)

    # Ensure number of learners has increased
    body = tests.utils.get_rest_api_client(rest_api_client, str_path_instructor,
                                           'List instructors from a course', 'RESPONSE:', 200)
    assert n_instructors + 1 == body['count']
    ''''''
    # TODO Remove an instructor from course but not from system (from instructor privileges)
    '''
    # str_path = '/api/v2/institution/{}/course/{}/instructor/{}/'.format(institution_id, course_id, new_instructor_id)
    tests.utils.delete_rest_api_client(rest_api_client, str_path_instructor,
                                       'Delete Instructor from a Course', "RESPONSE: ", 204)
    assert body['count'] == n_instructors
    '''
    pytest.skip('TODO')
