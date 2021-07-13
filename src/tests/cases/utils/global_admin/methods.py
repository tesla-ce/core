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
""" TeSLA CE Global Administrator actions for Use Case tests """
import json

from tests import auth_utils
from tests.conftest import get_random_string
from tests.utils import get_provider_desc_file


def api_register_providers(global_admin):
    """
        A global administrator register the providers
        :param global_admin: Global admin object
        :return: Registered providers
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Get the list of instruments
    instruments = []
    stop = False
    while not stop:
        list_instruments_resp = client.get('/api/v2/admin/instrument/?offset={}'.format(len(instruments)))
        assert list_instruments_resp.status_code == 200
        instruments += list_instruments_resp.data['results']

        if len(instruments) == list_instruments_resp.data['count']:
            stop = True

    # Get the instruments we want to register
    fr_inst = None
    ks_inst = None
    plag_inst = None

    # Remove any existing provider
    for instrument in instruments:
        if instrument['acronym'] == 'fr':
            fr_inst = instrument['id']
        if instrument['acronym'] == 'ks':
            ks_inst = instrument['id']
        if instrument['acronym'] == 'plag':
            plag_inst = instrument['id']
        stop = False
        while not stop:
            list_inst_providers_resp = client.get('/api/v2/admin/instrument/{}/provider/'.format(instrument['id']))
            assert list_inst_providers_resp.status_code == 200
            if list_inst_providers_resp.data['count'] > 0:
                for inst_prov in list_inst_providers_resp.data['results']:
                    del_providers_resp = client.delete(
                        '/api/v2/admin/instrument/{}/provider/{}/'.format(instrument['id'], inst_prov['id'])
                    )
                    assert del_providers_resp.status_code == 204
            else:
                stop = True

    providers = {}

    # Register a FR provider
    fr_desc = json.load(open(get_provider_desc_file('fr_tfr'), 'r'))
    fr_desc['enabled'] = True
    fr_desc['validation_active'] = True
    if 'instrument' in fr_desc:
        del fr_desc['instrument']
    fr_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(fr_inst),
                                        data=fr_desc,
                                        format='json')
    assert fr_prov_register_resp.status_code == 201
    providers['fr'] = fr_prov_register_resp.data
    providers['fr']['deferred'] = False

    # Register a FR provider that use deferred analysis
    fr_desc2 = json.load(open(get_provider_desc_file('fr_amazon'), 'r'))
    fr_desc2['enabled'] = True
    fr_desc2['validation_active'] = True
    if 'instrument' in fr_desc2:
        del fr_desc2['instrument']
    fr_prov2_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(fr_inst),
                                         data=fr_desc2,
                                         format='json')
    assert fr_prov2_register_resp.status_code == 201
    providers['fr_def'] = fr_prov2_register_resp.data
    providers['fr_def']['deferred'] = True

    # Register a KS provider
    ks_desc = json.load(open(get_provider_desc_file('ks_tks'), 'r'))
    ks_desc['enabled'] = True
    ks_desc['validation_active'] = True
    if 'instrument' in ks_desc:
        del ks_desc['instrument']
    ks_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(ks_inst),
                                        data=ks_desc,
                                        format='json')
    assert ks_prov_register_resp.status_code == 201
    providers['ks'] = ks_prov_register_resp.data
    providers['ks']['deferred'] = False

    # Register a Plagiarism provider
    pt_desc = json.load(open(get_provider_desc_file('pt_tpt'), 'r'))
    pt_desc['enabled'] = True
    if 'instrument' in pt_desc:
        del pt_desc['instrument']
    pt_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(plag_inst),
                                        data=pt_desc,
                                        format='json')
    assert pt_prov_register_resp.status_code == 201
    providers['plag'] = pt_prov_register_resp.data
    providers['plag']['deferred'] = False

    # Register a Plagiarism provider with deferred processing
    pt_desc2 = json.load(open(get_provider_desc_file('pt_turkund'), 'r'))
    pt_desc2['enabled'] = True
    if 'instrument' in pt_desc2:
        del pt_desc2['instrument']
    pt2_prov_register_resp = client.post('/api/v2/admin/instrument/{}/provider/'.format(plag_inst),
                                         data=pt_desc2,
                                         format='json')
    assert pt2_prov_register_resp.status_code == 201
    providers['plag_def'] = pt2_prov_register_resp.data
    providers['plag_def']['deferred'] = True

    # Enable the instruments
    fr_inst_enable_resp = client.patch('/api/v2/admin/instrument/{}/'.format(fr_inst),
                                       data={'enabled': True},
                                       format='json')
    assert fr_inst_enable_resp.status_code == 200
    ks_inst_enable_resp = client.patch('/api/v2/admin/instrument/{}/'.format(ks_inst),
                                       data={'enabled': True},
                                       format='json')
    assert ks_inst_enable_resp.status_code == 200
    pt_inst_enable_resp = client.patch('/api/v2/admin/instrument/{}/'.format(plag_inst),
                                       data={'enabled': True},
                                       format='json')
    assert pt_inst_enable_resp.status_code == 200

    return providers


def api_create_institution(global_admin, external_ic=False):
    """
        A global admin creates a new institution
        :param global_admin: Global admin object
        :param external_ic: True if the IC is managed externally, and assumed accepted, False otherwise
        :return: New created institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Create a new institution
    institution_data = {
        'name': "PyTest Test institution {}".format(get_random_string(5)),
        'acronym': get_random_string(10),
        'external_ic': external_ic
    }
    inst_create_resp = client.post('/api/v2/admin/institution/', data=institution_data, format='json')
    assert inst_create_resp.status_code == 201

    # Get institution object
    institution = inst_create_resp.data

    return institution


def api_create_institution_admin(global_admin, institution):
    """
        A global administrator creates a new user for the institution and assign administration rights
        :param global_admin: Global admin object
        :param institution: Institution object
        :return: New created institution
    """
    # Set global admin user.
    client = auth_utils.client_with_user_obj(global_admin)

    # Create a new user
    user_name = get_random_string(10)
    password = get_random_string(10)
    email = '{}@tesla-ce.eu'.format(user_name)
    user_data = {
        'username': user_name,
        'uid': user_name,
        'email': email,
        'first_name': user_name[:5],
        'last_name': user_name[5:],
        'institution_id': institution['id'],
        'login_allowed': True,
        'is_active': True,
        'is_staff': False,
        'password': password,
        'password2': password,
        'inst_admin': True
    }
    user_create_resp = client.post('/api/v2/admin/user/', data=user_data, format='json')
    assert user_create_resp.status_code == 201

    # Get institution admin object
    admin_user = user_create_resp.data
    assert 'ADMIN' in admin_user['roles']
    assert admin_user['institution']['id'] == institution['id']

    # Return credentials
    return {
        'email': email,
        'password': password
    }
