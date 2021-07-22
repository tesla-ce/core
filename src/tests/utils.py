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
import os
import logging
import pytest


# Check that ALL unauthenticated users are not allowed
def check_403(rest_api_client, str_path, users=None):
    """

    @param rest_api_client:
    @param str_path: path for checking non allowed users
    @param users: list of non allowed users
    """
    # Check that unauthenticated calls are not allowed
    if users is None:
        users = []
    response_403 = rest_api_client.get(str_path)
    assert response_403.status_code == 403

    # Check that global admins can list the instruments
    for usr in users:
        rest_api_client.force_authenticate(user=usr)
        response_403 = rest_api_client.get(str_path)
        assert response_403.status_code == 403


def print_log(args):
    """

    @param args: list of messages for logging. First item on list is the current testing module name.
    """
    module = ''
    if len(args) > 0:
        module = '[{}] '.format(args[0][0])
        # module = '[' + args[0][0] + '] '
    for i in range(1, len(args)):
        aux = module
        for j in args[i]:
            aux += str(j) + ' '
        logging.info(aux)


@pytest.mark.django_db
def get_rest_api_client(rest_api_client, str_path, module, message, status):
    """

    @param rest_api_client:
    @param str_path: GET path
    @param module: Testing module name
    @param message: Logging info message
    @param status: Testing status (example: 200, 404...)
    @return: response body
    """
    response = rest_api_client.get(str_path, format='json')
    body = response.json()
    str_log = [[module], ['Expected Status:', status],
               ['Received Status:', response.status_code], [message, body]]
    print_log(str_log)
    assert response.status_code == status
    return body


@pytest.mark.django_db
def post_rest_api_client(rest_api_client, str_path, str_data, module, message, status):
    """

    @param rest_api_client:
    @param str_path:
    @param str_data:
    @param module: Testing module name
    @param message: Logging info message
    @param status: Testing status (example: 200, 404...)
    @return: New item ID (-1 if creation failed)
    """
    response = rest_api_client.post(str_path, data=str_data, format='json')
    body = response.json()
    str_log = [[module], ['POST data:', str_data], ['Expected Status:', status],
               ['Received Status:', response.status_code], [message, body]]
    print_log(str_log)
    assert response.status_code == status
    if status == 201:
        new_item_id = response.json()['id']
        str_log.append(['NEW ITEM ID:', new_item_id])
    else:
        new_item_id = -1
    print_log(str_log)
    return new_item_id


@pytest.mark.django_db
def put_rest_api_client(rest_api_client, str_path, str_data, module, message, status):
    """

    @param rest_api_client:
    @param str_path:
    @param str_data:
    @param module: Testing module name
    @param message: Logging info message
    @param status: Testing status (example: 200, 404...)
    """
    response = rest_api_client.put(str_path, data=str_data, format='json')
    body = response.json()

    str_log = [[module], ['PUT item:', str_path], ['PUT data:', str_data],
               ['Expected Status:', status],
               ['Received Status:', response.status_code], [message, body]]
    print_log(str_log)
    assert response.status_code == status


@pytest.mark.django_db
def delete_rest_api_client(rest_api_client, str_path, module, message, status):
    """

    @param rest_api_client:
    @param str_path:
    @param module: Testing module name
    @param message: Logging info message
    @param status: Testing status (example: 200, 404...)
    """
    response = rest_api_client.delete(str_path)
    str_log = [[module], ['Expected Status:', status],
               ['Received Status:', response.status_code], [message, response],
               ['response.status_code', response.status_code]]
    print_log(str_log)
    assert response.status_code == status


def check_pagination(rest_api_client, body):
    body_aux = body
    offset = len(body_aux['results'])
    print_log([['Check pagination'], ['offset: ', offset]])
    while body_aux['next'] is not None:
        body_aux = get_rest_api_client(rest_api_client, body_aux['next'], 'Check pagination', 'Next page:', 200)
        offset = offset + len(body_aux['results'])
        print_log([['Check pagination'], ['offset: ', offset]])
    assert offset == body['count']


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
def get_profile(rest_api_client, token):
    """
        Get authenticated user profile
        :param rest_api_client: API client
        :param token: Access token
        :return: Returned profile
    """
    rest_api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
    profile_resp = rest_api_client.get('/api/v2/auth/profile')
    rest_api_client.credentials()

    return profile_resp


def get_provider_desc_file(provider):
    """
        Get the path to the file with the provider description
        :param provider: Provider name
        :return: Path to the file
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                           '..', '..', 'providers', '{}.json'.format(provider)))


def get_module_auth_user(module):
    """
        Get a module authentication object from a object module instance
        :param module: Module object
        :return: Authentication object
    """
    from tesla_ce.models import VLE, Provider, AuthenticatedModule
    auth_object = None
    if isinstance(module, VLE) or isinstance(module, Provider):
        auth_object = AuthenticatedModule()
        auth_object.id = module.id
        auth_object.pk = module.id
        auth_object.module = module
        if isinstance(module, VLE):
            auth_object.type = 'vle'
        else:
            auth_object.type = 'provider'
    return auth_object
