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
    response = rest_api_client.get(str_path)
    body = response.json()
    assert response.status_code == status
    str_log = [[module], ['Status:', status], [message, body]]
    print_log(str_log)
    return body


@pytest.mark.django_db
def post_rest_api_client(rest_api_client, str_path, str_data, module, message, status):
    """

    @param rest_api_client:
    @param str_path:
    @param str_data:
    @param module:
    @param message:
    @param status:
    @return:
    """
    response = rest_api_client.post(str_path, data=str_data)
    body = response.json()
    str_log = [[module], ['POST data:', str_data], ['Status:', status], [message, body]]
    assert response.status_code == status
    if status == 201:
        new_instrument_id = response.json()['id']
        str_log.append(['NEW INSTRUMENT ID:', new_instrument_id])
    else:
        new_instrument_id = -1
    print_log(str_log)
    return new_instrument_id


@pytest.mark.django_db
def put_rest_api_client(rest_api_client, str_path, str_data, module, message, status):
    """

    @param rest_api_client:
    @param str_path:
    @param str_data:
    @param module:
    @param message:
    @param status:
    """
    response = rest_api_client.put(str_path, data=str_data)
    body = response.json()

    str_log = [[module], ['PUT item:', str_path], ['PUT data:', str_data],
               ['Status:', status], [message, body]]
    print_log(str_log)
    assert response.status_code == status


@pytest.mark.django_db
def delete_rest_api_client(rest_api_client, str_path, module, message, status):
    """

    @param rest_api_client:
    @param str_path:
    @param module:
    @param message:
    @param status:
    """
    response = rest_api_client.delete(str_path)
    str_log = [[module], ['Status:', status], [message]]
    print_log(str_log)
    assert response.status_code == status


def print_log(args):
    """

    @param args: list of messages for logging. First item on list is the current testing module name.
    """
    module = ''
    if len(args) > 0:
        module = '[' + args[0][0] + '] '
    for i in range(1, len(args)):
        aux = module
        for j in args[i]:
            aux += str(j) + ' '
        logging.info(aux)


def check_pagination(rest_api_client, body):
    body_aux = body
    offset = len(body_aux['results'])
    print_log([['Check pagination'], ['offset: ', offset]])
    while body_aux['next'] is not None:
        body_aux = get_rest_api_client(rest_api_client, body_aux['next'], 'Check pagination', 'Next page:', 200)
        offset = offset + len(body_aux['results'])
        print_log([['Check pagination'], ['offset: ', offset]])
    assert offset == body['count']



