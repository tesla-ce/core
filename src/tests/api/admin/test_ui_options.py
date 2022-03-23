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
""" Module for Authentication API profile """
import pytest
import tests
from tests.utils import get_profile


@pytest.mark.django_db
def test_api_admin_ui_routes(rest_api_client, api_client, institution_course_test_case,
                             user_global_admin, empty_ui_routes):

    # Ensure there is no option defined
    rest_api_client.force_authenticate(user=user_global_admin)
    options_list = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/ui/',
                                                   'List ui options', 'RESPONSE:', 200)
    assert options_list['count'] == 0

    # Add a basic route for all users
    options_add = rest_api_client.post('/api/v2/admin/ui/', format='json', data={
        'enabled': True,
        'route': '/dashboard'
    })
    assert options_add.status_code == 201

    # Add an option for admins
    options_add_admin = rest_api_client.post('/api/v2/admin/ui/', format='json', data={
        'enabled': True,
        'route': '/admin',
        'roles': 'GLOBAL_ADMIN'
    })
    assert options_add_admin.status_code == 201

    options_list = tests.utils.get_rest_api_client(rest_api_client, '/api/v2/admin/ui/',
                                                   'List ui options', 'RESPONSE:', 200)
    assert options_list['count'] == 2
    assert options_list['results'][0]['route'] == '/dashboard' or options_list['results'][0]['route'] == '/admin'
    if options_list['results'][0]['route'] == '/admin':
        assert options_list['results'][1]['roles'] is None
        assert options_list['results'][0]['roles'] == 'GLOBAL_ADMIN'
    else:
        assert options_list['results'][0]['roles'] is None
        assert options_list['results'][1]['roles'] == 'GLOBAL_ADMIN'

    # Check profile routes
    # Global Admin
    global_admin_token = api_client.get_admin_token_pair(user_global_admin, {})
    global_admin_profile_resp = get_profile(rest_api_client, global_admin_token['access_token'])
    assert global_admin_profile_resp.status_code == 200
    assert 'routes' in global_admin_profile_resp.data
    assert len(global_admin_profile_resp.data['routes']) == 2
    assert '/admin' in global_admin_profile_resp.data['routes']
    assert '/dashboard' in global_admin_profile_resp.data['routes']

    # Institution user
    inst_user_token = api_client.get_user_token_pair(institution_course_test_case['user'].institutionuser, {})
    inst_user_profile_resp = get_profile(rest_api_client, inst_user_token['access_token'])
    assert inst_user_profile_resp.status_code == 200
    assert 'routes' in inst_user_profile_resp.data
    assert len(inst_user_profile_resp.data['routes']) == 1
    assert '/dashboard' in inst_user_profile_resp.data['routes']

    # Add learners and instructors routes
    options_add_courses = rest_api_client.post('/api/v2/admin/ui/', format='json', data={
        'enabled': True,
        'route': '/mycourses',
        'roles': 'LEARNER,INSTRUCTOR'
    })
    assert options_add_courses.status_code == 201

    # Check that new route is not included for global admins
    global_admin_profile_resp = get_profile(rest_api_client, global_admin_token['access_token'])
    assert global_admin_profile_resp.status_code == 200
    assert len(global_admin_profile_resp.data['routes']) == 2
    assert '/mycourses' not in global_admin_profile_resp.data['routes']
    assert '/admin' in global_admin_profile_resp.data['routes']
    assert '/dashboard' in global_admin_profile_resp.data['routes']

    # Check that new route is not included for institution admins
    inst_user_token = api_client.get_user_token_pair(institution_course_test_case['user'].institutionuser, {})
    inst_user_profile_resp = get_profile(rest_api_client, inst_user_token['access_token'])
    assert inst_user_profile_resp.status_code == 200
    assert len(inst_user_profile_resp.data['routes']) == 1
    assert '/mycourses' not in inst_user_profile_resp.data['routes']
    assert '/dashboard' in inst_user_profile_resp.data['routes']

    # Check that is included for learners
    learner_user = institution_course_test_case['learner'].institutionuser.learner
    inst_learner_user_token = api_client.get_user_token_pair(learner_user, {})
    inst_learner_user_profile_resp = get_profile(rest_api_client, inst_learner_user_token['access_token'])

    assert inst_learner_user_profile_resp.status_code == 200
    assert 'routes' in inst_learner_user_profile_resp.data
    assert len(inst_learner_user_profile_resp.data['routes']) == 2
    assert '/dashboard' in inst_learner_user_profile_resp.data['routes']
    assert '/mycourses' in inst_learner_user_profile_resp.data['routes']

    # Check that is included for instructors
    instructor_user = institution_course_test_case['instructor'].institutionuser.instructor
    inst_instructor_user_token = api_client.get_user_token_pair(instructor_user, {})
    inst_instructor_user_profile_resp = get_profile(rest_api_client, inst_instructor_user_token['access_token'])

    assert inst_instructor_user_profile_resp.status_code == 200
    assert 'routes' in inst_instructor_user_profile_resp.data
    assert len(inst_instructor_user_profile_resp.data['routes']) == 2
    assert '/dashboard' in inst_instructor_user_profile_resp.data['routes']
    assert '/mycourses' in inst_instructor_user_profile_resp.data['routes']
