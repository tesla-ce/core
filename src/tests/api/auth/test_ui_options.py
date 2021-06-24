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
from tests.utils import get_profile


@pytest.mark.django_db
def test_api_authentication_profile_routes(rest_api_client, api_client, institution_course_test_case,
                                           user_global_admin, base_ui_routes):

    # Get global admin token
    global_admin_token = api_client.get_admin_token_pair(user_global_admin, {})
    assert global_admin_token is not None
    assert 'access_token' in global_admin_token
    global_admin_profile_resp = get_profile(rest_api_client, global_admin_token['access_token'])
    assert global_admin_profile_resp.status_code == 200
    assert 'routes' in global_admin_profile_resp.data
    assert '/admin' in global_admin_profile_resp.data['routes']
    assert '/dashboard' in global_admin_profile_resp.data['routes']
    assert '/mycourses' not in global_admin_profile_resp.data['routes']
    assert '/inst_admin' not in global_admin_profile_resp.data['routes']

    # Get institution user token
    inst_user_token = api_client.get_user_token_pair(institution_course_test_case['user'].institutionuser, {})
    assert inst_user_token is not None
    assert 'access_token' in inst_user_token
    inst_user_profile_resp = get_profile(rest_api_client, inst_user_token['access_token'])
    assert inst_user_profile_resp.status_code == 200
    assert 'institution' in inst_user_profile_resp.data
    assert 'routes' in inst_user_profile_resp.data
    assert len(inst_user_profile_resp.data['routes']) == 1

    # Get institution admin token
    admin_user = institution_course_test_case['user'].institutionuser
    admin_user.inst_admin = True
    admin_user.data_admin = True
    admin_user.legal_admin = True
    admin_user.send_admin = True
    admin_user.save()

    inst_admin_user_token = api_client.get_user_token_pair(admin_user, {})
    assert inst_admin_user_token is not None
    assert 'access_token' in inst_admin_user_token
    inst_admin_user_profile_resp = get_profile(rest_api_client, inst_admin_user_token['access_token'])
    assert inst_admin_user_profile_resp.status_code == 200
    assert 'institution' in inst_admin_user_profile_resp.data
    assert 'routes' in inst_admin_user_profile_resp.data
    assert '/admin' not in inst_admin_user_profile_resp.data['routes']
    assert '/dashboard' in inst_admin_user_profile_resp.data['routes']
    assert '/mycourses' not in inst_admin_user_profile_resp.data['routes']
    assert '/inst_admin' in inst_admin_user_profile_resp.data['routes']

    # Get institution learner token
    learner_user = institution_course_test_case['learner'].institutionuser.learner

    inst_learner_user_token = api_client.get_user_token_pair(learner_user, {})
    assert inst_learner_user_token is not None
    assert 'access_token' in inst_learner_user_token
    inst_learner_user_profile_resp = get_profile(rest_api_client, inst_learner_user_token['access_token'])
    assert inst_learner_user_profile_resp.status_code == 200
    assert 'institution' in inst_learner_user_profile_resp.data
    assert 'routes' in inst_learner_user_profile_resp.data
    assert '/admin' not in inst_learner_user_profile_resp.data['routes']
    assert '/dashboard' in inst_learner_user_profile_resp.data['routes']
    assert '/mycourses' in inst_learner_user_profile_resp.data['routes']
    assert '/inst_admin' not in inst_learner_user_profile_resp.data['routes']

    # Get institution instructor token
    instructor_user = institution_course_test_case['instructor'].institutionuser.instructor

    inst_instructor_user_token = api_client.get_user_token_pair(instructor_user, {})
    assert inst_instructor_user_token is not None
    assert 'access_token' in inst_learner_user_token
    inst_instructor_user_profile_resp = get_profile(rest_api_client, inst_instructor_user_token['access_token'])
    assert inst_instructor_user_profile_resp.status_code == 200
    assert 'institution' in inst_instructor_user_profile_resp.data
    assert 'routes' in inst_instructor_user_profile_resp.data
    assert '/admin' not in inst_instructor_user_profile_resp.data['routes']
    assert '/dashboard' in inst_instructor_user_profile_resp.data['routes']
    assert '/mycourses' in inst_instructor_user_profile_resp.data['routes']
    assert '/inst_admin' not in inst_instructor_user_profile_resp.data['routes']
