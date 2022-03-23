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
""" DJango Configuration tests module """
import os
import mock
from tesla_ce.settings import Production, Dev
from tesla_ce.lib import ConfigManager
from tesla_ce.lib.modules import get_modules


def check_config(settings_cls, module, debug=False, worker=False):
    """
        Check configuration class values
        :param settings_cls: The configuration class
        :param module: The name of the module
        :param debug: If configuration should have debug enabled
        :param worker: If configuration corresponds to a worker
    """
    assert settings_cls.DEBUG == debug
    assert settings_cls.TESLA_CONFIG is not None
    assert len(settings_cls.TESLA_MODULES) == 1
    assert module in settings_cls.TESLA_MODULES
    assert len(settings_cls.TESLA_CONFIG.enabled_modules) == 1
    assert module in settings_cls.TESLA_CONFIG.enabled_modules
    assert len(settings_cls.TESLA_CONFIG.modules) == 1
    assert module in settings_cls.TESLA_CONFIG.modules
    assert settings_cls.TESLA_CONFIG.modules[module]['module'] == module

    if worker:
        assert settings_cls.CELERY_BROKER_URL is not None
        # assert settings_cls.AWS_ACCESS_KEY_ID is not None
        # assert settings_cls.AWS_SECRET_ACCESS_KEY is not None


def get_available_modules():
    """
        Get the list of modules and workers defined in TeSLA CE
        :return: Tuple with modules and workers names
    """
    modules = []
    workers = []
    available_modules = get_modules()
    for module in available_modules:
        modules.append(module)
        if 'type' in available_modules[module]['deployment'] and \
                available_modules[module]['deployment']['type'] == 'worker':
            workers.append(module)

    return modules, workers


def test_production_config(admin_client):
    modules, workers = get_available_modules()
    for module in modules:
        creds = admin_client.vault.get_module_credentials(module)
        with mock.patch.dict(os.environ, {
            "VAULT_URL": admin_client.config.config.get('VAULT_URL'),
            "VAULT_ROLE_ID": creds['role_id'],
            "VAULT_SECRET_ID": creds['secret_id']
        }, clear=True):
            Production.TESLA_CONFIG = ConfigManager()
            Production.pre_setup()
            Production.post_setup()
            is_worker = module in workers
            check_config(Production, module, debug=False, worker=is_worker)


def test_dev_config(admin_client):
    modules, workers = get_available_modules()
    for module in modules:
        creds = admin_client.vault.get_module_credentials(module)
        with mock.patch.dict(os.environ, {
            "VAULT_URL": admin_client.config.config.get('VAULT_URL'),
            "VAULT_ROLE_ID": creds['role_id'],
            "VAULT_SECRET_ID": creds['secret_id']
        }, clear=True):
            Dev.TESLA_CONFIG = ConfigManager()
            Dev.pre_setup()
            Dev.post_setup()
            is_worker = module in workers
            check_config(Dev, module, debug=True, worker=is_worker)


def test_dev_config_multiple(admin_client):
    token = admin_client.config.config.get('VAULT_TOKEN')
    with mock.patch.dict(os.environ, {
        "VAULT_URL": admin_client.config.config.get('VAULT_URL'),
        "VAULT_TOKEN": token,
        "TESLA_RUN_AS_MODULE": 'api,lapi',
        "RABBITMQ_ADMIN_USER": admin_client.config.config.get('RABBITMQ_ADMIN_USER'),
        "RABBITMQ_ADMIN_PASSWORD": admin_client.config.config.get('RABBITMQ_ADMIN_PASSWORD')
    }):
        Dev.TESLA_CONFIG = ConfigManager()
        Dev.pre_setup()
        Dev.post_setup()

        assert len(Dev.TESLA_MODULES) == 2
        assert 'api' in Dev.TESLA_MODULES
        assert 'lapi' in Dev.TESLA_MODULES
