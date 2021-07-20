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
import logging

import pytest

import tests.utils

from tests.utils import getting_variables


@pytest.mark.django_db
def test_api_institution_course_learners(rest_api_client, user_global_admin, institution_course_test_case):
    # pytest.skip('TODO')
    # institution
    institution_id = institution_course_test_case['institution'].id
    # institution user
    institution_user = institution_course_test_case['user'].institutionuser
    institution_user_id = institution_user.id
    institution_user_uid = institution_user.uid
    # instructor
    instructor = institution_course_test_case['instructor']
    instructor_user = instructor.institutionuser
    instructor_user_id = instructor_user.id
    # learner
    learner = institution_course_test_case['learner']
    learner_user = learner.institutionuser
    learner_user_id = learner_user.id

    # Get the list of courses for an instructor
    rest_api_client.force_authenticate(user=learner_user)

    '''
     # Get the list of courses for a normal Institution User not belonging to any course
     institution_user = institution_course_test_case['user'].institutionuser
     institution_user.inst_admin = False
     institution_user.data_admin = False
     institution_user.save()
     rest_api_client.force_authenticate(user=institution_user)
     inst_admin_resp = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                       'List Courses Inst User', 'RESPONSE:', 200)
     assert inst_admin_resp['count'] == 0
     '''

    # TODO Course Learners
    # TODO List learners from a course
    # Get the list of courses for a learner
    rest_api_client.force_authenticate(user=learner_user)
    courses_url = '/api/v2/institution/{}/course/'.format(institution_id)
    str_module = 'List of Instructor\'s Courses (Learner user privileges)'
    str_message = 'RESPONSE institution_id:{} learner_user_id:{}'.format(institution_id, learner_user_id)
    courses_list = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                   str_module, str_message, 200)
    n_courses = courses_list['count']
    assert n_courses == 1

    # Select first course
    course_id = courses_list['results'][0]['id']

    # Get the list of learners for a learner's course
    str_path = '/api/v2/institution/{}/course/{}/learner/'.format(institution_id, course_id)
    str_module = 'List learners from a course (learner user privileges)'
    str_message = 'RESPONSE institution_id:{} course_id:{} learner_user_id:{}'.format(institution_id, course_id, learner_user_id)
    body = tests.utils.get_rest_api_client(rest_api_client, str_path,
                                           str_module, str_message, 200)
    assert body['count'] == 1
    assert body['results'][0]['id'] == learner_user_id

    # List instructors from a course
    courses_url = '/api/v2/institution/{}/course/{}/instructor/'.format(institution_id, course_id)
    str_module = 'List of Course\'s Instructors (Learner user privileges)'
    str_message = 'RESPONSE institution_id:{} course_id:{} learner_user_id:{}'.format(institution_id, course_id, learner_user_id)
    instructors_list = tests.utils.get_rest_api_client(rest_api_client, courses_url,
                                                       str_module, str_message, 200)
    n_instructors = instructors_list['count']
    assert n_instructors == 1
    assert instructors_list['results'][0]['id'] == instructor_user_id

    # TODO Create a new Learner: add learner to a course (institution admin)
    # TODO Delete learner: remove from course but not from system (institution admin)
    # TODO a learner can list instructors from her own course
    # TODO a learner can read her own information




