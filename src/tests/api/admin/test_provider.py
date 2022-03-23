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
""" Tests for providers administration """
import pytest

import mock

from tests.conftest import get_random_string


@pytest.mark.django_db
def test_api_admin_providers(rest_api_client, user_global_admin, institution_course_test_case):
    # Ensure that only GLOBAL_ADMINS have access
    users = [
        None,
        institution_course_test_case['user'],
        institution_course_test_case['instructor'],
        institution_course_test_case['learner']
    ]
    for instrument in range(4):
        for user in users:
            rest_api_client.force_authenticate(user=user)
            no_auth_resp = rest_api_client.get('/api/v2/admin/instrument/{}/provider/'.format(instrument))
            assert no_auth_resp.status_code == 403

    # User GLOBAL_ADMIN
    for instrument in range(4):
        rest_api_client.force_authenticate(user=user_global_admin)
        valid_auth_resp = rest_api_client.get('/api/v2/admin/instrument/{}/provider/'.format(instrument))
        assert valid_auth_resp.status_code == 200

    # Register a new provider
    rest_api_client.force_authenticate(user=user_global_admin)
    prov_acronym = 'fr_tfr_{}'.format(get_random_string(5))
    prov_data = {
        'acronym':  prov_acronym,
        'version': '0.0.5',
        'url': 'https://providers.tesla-project.eu/{}'.format(prov_acronym),
        'image': 'teslace/provider-{}'.format(prov_acronym),
        'name': 'TeSLA CE TEST PROVIDER',
        'description': 'A test provider for TeSLA CE automated tests',
        'has_service': False,
        'service_port': None,
        'options_schema': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'option1': {
                    'type': 'number', 'default': 1
                },
                'option2': {
                        'type': 'string', 'default': 'default value'
                },
            }
        },
        'options': {
            'option1': 3
        },
        'queue': prov_acronym,
        'allow_validation': True,
        'alert_below': 0.3,
        'warning_below': 0.6,
        'inverted_polarity': False,
        'enabled': False,
        'validation_active': False
    }

    new_provider_resp = rest_api_client.post('/api/v2/admin/instrument/{}/provider/'.format(1),
                                             data=prov_data, format='json')
    assert new_provider_resp.status_code == 201
    assert 'credentials' in new_provider_resp.data
    assert new_provider_resp.data['credentials'] is not None
    assert 'role_id' in new_provider_resp.data['credentials']
    assert 'secret_id' in new_provider_resp.data['credentials']

    # Check that this provider exists
    search_provider_resp = rest_api_client.get(
        '/api/v2/admin/instrument/{}/provider/?acronym={}'.format(1, prov_acronym)
    )
    assert search_provider_resp.status_code == 200
    assert search_provider_resp.data['count'] == 1
    assert search_provider_resp.data['results'][0]['id'] == new_provider_resp.data['id']

    # Update options with a valid schema
    update_provider_resp = rest_api_client.patch(
        '/api/v2/admin/instrument/{}/provider/{}/'.format(1, new_provider_resp.data['id']),
        format='json',
        data={'options': {'option1': 35}}
    )
    assert update_provider_resp.status_code == 200
    assert update_provider_resp.data['options']['option1'] == 35

    inv_update_provider_resp = rest_api_client.patch(
        '/api/v2/admin/instrument/{}/provider/{}/'.format(1, new_provider_resp.data['id']),
        format='json',
        data={'options': {'option1': 'a'}}
    )
    assert inv_update_provider_resp.status_code == 400
    assert 'non_field_errors' in inv_update_provider_resp.data
    assert len(inv_update_provider_resp.data['non_field_errors']) == 1
    assert 'option1' in inv_update_provider_resp.data['non_field_errors'][0]

    inv2_update_provider_resp = rest_api_client.patch(
        '/api/v2/admin/instrument/{}/provider/{}/'.format(1, new_provider_resp.data['id']),
        format='json',
        data={'options': {'option3': 'a'}}
    )
    assert inv2_update_provider_resp.status_code == 400
    assert 'non_field_errors' in inv2_update_provider_resp.data
    assert len(inv2_update_provider_resp.data['non_field_errors']) == 1
    assert 'option3' in inv2_update_provider_resp.data['non_field_errors'][0]

    inv3_update_provider_resp = rest_api_client.patch(
        '/api/v2/admin/instrument/{}/provider/{}/'.format(1, new_provider_resp.data['id']),
        format='json',
        data={'options_schema': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'option51': {
                    'type': 'number', 'default': 1
                },
                'option52': {
                    'type': 'string', 'default': 'default value'
                },
            }
        }
    })
    assert inv3_update_provider_resp.status_code == 400
    assert 'non_field_errors' in inv3_update_provider_resp.data
    assert len(inv3_update_provider_resp.data['non_field_errors']) == 1
    assert 'option1' in inv3_update_provider_resp.data['non_field_errors'][0]

    inv4_update_provider_resp = rest_api_client.patch(
        '/api/v2/admin/instrument/{}/provider/{}/'.format(1, new_provider_resp.data['id']),
        format='json',
        data={'options_schema': None })
    assert inv4_update_provider_resp.status_code == 400
    assert 'non_field_errors' in inv4_update_provider_resp.data
    assert len(inv4_update_provider_resp.data['non_field_errors']) == 1
    assert 'NULL' in inv4_update_provider_resp.data['non_field_errors'][0]


def make_fail(self, provider_info, force_update=False):
    from tesla_ce.lib.exception import TeslaVaultException
    raise TeslaVaultException('test exception')


@pytest.mark.django_db
def test_api_admin_providers_fail(rest_api_client, user_global_admin):

    # Ensure provider is not registered in case of exception
    rest_api_client.force_authenticate(user=user_global_admin)
    prov_acronym = 'fr_tfr_{}'.format(get_random_string(5))
    prov_data = {
        'acronym':  prov_acronym,
        'version': '0.0.5',
        'url': 'https://providers.tesla-project.eu/{}'.format(prov_acronym),
        'image': 'teslace/provider-{}'.format(prov_acronym),
        'name': 'TeSLA CE TEST PROVIDER',
        'description': 'A test provider for TeSLA CE automated tests',
        'has_service': False,
        'service_port': None,
        'options_schema': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'option1': {
                    'type': 'number', 'default': 1
                },
                'option2': {
                        'type': 'string', 'default': 'default value'
                },
            }
        },
        'options': {
            'option1': 3
        },
        'queue': prov_acronym,
        'allow_validation': True,
        'alert_below': 0.3,
        'warning_below': 0.6,
        'inverted_polarity': False,
        'enabled': False,
        'validation_active': False
    }

    with mock.patch('tesla_ce.client.Client.register_provider', make_fail):
        new_provider_resp = rest_api_client.post('/api/v2/admin/instrument/{}/provider/'.format(1),
                                                 data=prov_data, format='json')
        assert new_provider_resp.status_code == 403
        assert 'detail' in new_provider_resp.data
        assert new_provider_resp.data['detail'] == 'Cannot register Provider'

        # Check that this provider does not exist
        search_provider_resp = rest_api_client.get(
            '/api/v2/admin/instrument/{}/provider/?acronym={}'.format(1, prov_acronym)
        )
        assert search_provider_resp.status_code == 200
        assert search_provider_resp.data['count'] == 0
