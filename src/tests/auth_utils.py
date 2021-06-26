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
""" Module with authentication utils for tests """
from rest_framework.test import APIClient


def client_with_user_obj(user):
    """
        Get an API client instance authenticated with provided user
        :param user: User object
        :return: API Client instance
    """
    client = APIClient()
    client.force_authenticate(user=user)

    return client


def get_profile(client):
    """
        Get the profile of authenticated user
        :param client: API Client with user authentication
        :return: Profile data
    """
    # Get user profile
    profile_resp = client.get('/api/v2/auth/profile')
    assert profile_resp.status_code == 200

    return profile_resp.data


def client_with_user_credentials(email, password):
    """
        Get an API client instance authenticated with provided user credentials
        :param email: User's email
        :param password: User's password
        :return: API Client instance
    """
    client = APIClient()

    # TODO: Remove fake authentication
    password = email

    auth_resp = client.post('/api/v2/auth/login', data={
        'email': email,
        'password': password
    })
    assert auth_resp.status_code == 200
    assert 'token' in auth_resp.data

    # Assign credentials
    token = auth_resp.data['token']['access_token']
    client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))

    return client


def client_with_approle_credentials(role_id, secret_id):
    """
        Get an API client instance authenticated with provided AppRole module credentials
        :param role_id: The module's RoleID
        :param secret_id: The module's SecretID
        :return: A tuple (client, configuration) with the client instance and module configuration
    """
    client = APIClient()

    auth_resp = client.post('/api/v2/auth/approle', data={
        'role_id': role_id,
        'secret_id': secret_id
    })
    assert auth_resp.status_code == 200
    assert 'token' in auth_resp.data

    # Assign credentials
    token = auth_resp.data['token']['access_token']
    client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(token))

    return client, auth_resp.data

