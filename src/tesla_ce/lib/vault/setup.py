#  Copyright (c) 2020 Xavier Baró
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
""" Vault setup module """
import random
import string
import time

import hvac
from hvac.exceptions import InvalidPath
from hvac.exceptions import InvalidRequest

from .policies import get_policies
from .policies import get_service_config_map
from ..config.conf import Config
from ..modules import get_modules
from ..modules import get_provider_properties
from ..modules import get_vle_properties

# Template to generate module JWT key names
MODULE_KEY_STR_TEMPLATE = 'jwt_module_{}'


class VaultSetup:
    """ Class that defines the methods to setup Vault"""

    #: Vault client
    _client: hvac.Client = None

    #: Configuration object
    _config: Config = None

    def __init__(self, client, config):
        """
            Default constructor

            :param client: Vault client
            :type client: hvac.Client
            :param config: Configuration object
            :type config tesla-lib.config.conf.Config

        """
        self._client = client
        self._config = config

        # Read Vault mount points
        self._approle_mount_point = self._config.get('VAULT_MOUNT_PATH_APPROLE')
        self._transit_mount_point = self._config.get('VAULT_MOUNT_PATH_TRANSIT')
        self._kv_mount_point = self._config.get('VAULT_MOUNT_PATH_KV')
        self._policy_prefix = self._config.get('VAULT_POLICIES_PREFIX')

    def run_setup(self):
        """
            Perform Vault setup
        """
        # Setup KV
        self.setup_kv()

        # Update configuration
        self._update_configuration()

        # Setup JWT infrastructure
        self.setup_jwt()

        # Setup policies
        self.setup_policies()

        # Setup authentication roles
        self.setup_roles()

    def setup_kv(self):
        """
            Setup the Key-Value secrets engine
        """
        from tesla_ce.client import get_version

        # Enable KV engine
        if not self._is_secret_engine_enabled('{}/'.format(self._kv_mount_point)):
            self._client.sys.enable_secrets_engine('kv', path=self._kv_mount_point, options={'version': 2},
                                                   description='TeSLA CE Secrets Engine')
            # This can take a time to be ready. Wait until active
            time.sleep(2)
            ready = False
            max_try = 5
            while not ready and max_try > 0:
                try:
                    self._client.secrets.kv.v2.create_or_update_secret(
                        path='{}/{}'.format('system', 'version'),
                        secret=dict({
                            'tesla-ce': get_version()
                        }),
                        mount_point=self._kv_mount_point
                    )
                    ready = True
                except (InvalidRequest, InvalidRequest):
                    time.sleep(5)
                    max_try -= 1

        # Update system version and vault mount paths
        self._client.secrets.kv.v2.create_or_update_secret(
            path='{}/{}'.format('system', 'version'),
            secret=dict({
                'tesla-ce': get_version()
            }),
            mount_point=self._kv_mount_point
        )

        # Check secret keys
        if self._config.get('DJANGO_SECRET_KEY') is None:
            # Generate a new secret key
            key = ''.join([string.ascii_letters,
                           string.digits,
                           string.punctuation]).replace('\'', '').replace('"', '').replace('\\', '')
            key = ''.join([random.SystemRandom().choice(key) for _ in range(50)])
            self._config.set('DJANGO_SECRET_KEY', key)

        # Store configuration values
        config = self._config.get_config()
        for section in config:
            for key in config[section]:
                self._client.secrets.kv.v2.create_or_update_secret(
                    path='config/{}/{}'.format(section, key),
                    secret=dict(config[section][key]),
                    mount_point=self._kv_mount_point
                )

    def _adapt_policies_path(self, policies):
        """
            Move policies to the defined Vault mount paths
            :param policies: Dictionary of policies with standard paths
            :return: Dictionary containing the policies with modified paths
        """
        adapted_policies = {}
        for policy in policies:
            adapted_policies[policy] = {'path': {}}
            for key in policies[policy]['path']:
                adapted_path = key.replace(
                    '<kv_path>', self._kv_mount_point
                ).replace(
                    '<transit_path>', self._transit_mount_point
                ).replace(
                    '<approle_path>', self._approle_mount_point
                ).replace(
                    '<policy_prefix>', self._policy_prefix
                )
                adapted_policies[policy]['path'][adapted_path] = policies[policy]['path'][key]
        return adapted_policies

    def setup_policies(self):
        """
            Creates the policies to grant access to services
        """
        # Create generic policies
        policies = self._adapt_policies_path(get_policies())
        for policy in policies:
            self._client.sys.create_or_update_policy(
                name='{}{}'.format(self._policy_prefix, policy),
                policy=policies[policy],
            )

    def _create_jwt_key(self, key):
        """
            Create an encryption key if it does not exist

            :param key: Name of the key
            :type key: str
        """
        # Create the key if it does not exist
        try:
            self._client.secrets.transit.read_key(key, mount_point=self._transit_mount_point)
        except InvalidPath:
            self._client.secrets.transit.create_key(key, key_type='rsa-4096', mount_point=self._transit_mount_point)

    def setup_jwt(self):
        """
            Setup JWT infrastructure
        """
        # Enable transit secret backend
        if not self._is_secret_engine_enabled('{}/'.format(self._transit_mount_point)):
            self._client.sys.enable_secrets_engine('transit', path=self._transit_mount_point)

        # Create a default key if it does not exist
        self._create_jwt_key('jwt_default')

        # Create learners key if it does not exist
        self._create_jwt_key('jwt_learners')

        # Create instructors key if it does not exist
        self._create_jwt_key('jwt_instructors')

        # Create users key if it does not exist
        self._create_jwt_key('jwt_users')

        # Create modules key if it does not exist
        self._create_jwt_key('jwt_modules')

        # Create individual modules key if they do not exist
        for module in get_modules():
            self._create_jwt_key(MODULE_KEY_STR_TEMPLATE.format(module))

    def setup_roles(self):
        """
            Creates the roles for the different modules that needs to authenticate with Vault
        """
        if not self._is_auth_method_enabled('{}/'.format(self._approle_mount_point)):
            self._client.sys.enable_auth_method('approle', path=self._approle_mount_point,
                                                description='TeSLA CE modules authentication')

        modules = get_modules()
        for module in modules:
            self._create_module_entity(modules[module])

    def _is_secret_engine_enabled(self, mount):
        """
            Check if a Vault secret engine is enabled

            :param mount: Mount point of the secret engine
            :return: True if the secret engine is enabled or False otherwise
            :rtype: bool
        """
        secrets_engines_list = self._client.sys.list_mounted_secrets_engines()['data']

        for engine in secrets_engines_list:
            if engine == mount:
                return True
        return False

    def _is_auth_method_enabled(self, mount):
        """
            Check if a Vault authentication method is enabled

            :param mount: Mount point of the authentication method
            :return: True if the authentication method is enabled or False otherwise
            :rtype: bool
        """
        auth_methods_list = self._client.sys.list_auth_methods()['data']

        for method in auth_methods_list:
            if method == mount:
                return True
        return False

    @staticmethod
    def _add_generic_service_access(module, conf_map, config, policies):
        """
            Update initial list of policies and configuration values with the ones required for services
            :param module: Module information
            :param conf_map: Configuration map for the module
            :param config: Initial set of configuration values
            :param policies: Initial set of policies
            :return: Updated configuration and policies
        """
        for service in module['services']:
            roles = module['services'][service]
            if service in conf_map:
                for role in roles:
                    map_val = conf_map
                    for k in role.split('/'):
                        if k not in map_val:
                            map_val = None
                            break
                        map_val = map_val[k]
                    if map_val is not None:
                        for value in map_val['map']:
                            config.add(value)
                        policies.add(map_val['policy'])

        return config, policies

    def _build_config_and_policies(self, module):
        """
            Build the set of configurations and policies for a module
            :param module: Module information
            :return: Configuration set and policies
        """

        # Build configuration map and required policies
        policies = set()
        config = set()
        conf_map = get_service_config_map()

        # Add access to public configuration
        policies.add(conf_map['public']['policy'])
        for value in conf_map['public']['map']:
            config.add(value)

        # Add access to DJango configuration
        if 'django' in module['services']:
            policies.add('django_config')

        # Add default modules policy
        policies.add('modules_{}'.format(module['module']))

        # Add generic services access
        config, policies = self._add_generic_service_access(module, conf_map, config, policies)

        # Prepend policy prefix to policies
        policies = ['{}{}'.format(self._policy_prefix, policy) for policy in policies]

        return config, policies

    def _create_module_policy(self, module_name):
        """
            Create the default ACL for module
            :param module_name: Module name
        """

        module_policy = {
                'path': {
                    '{}/data/modules/{}/*'.format(self._kv_mount_point, module_name): {
                        'capabilities': ['read', 'list']
                    },
                    '{}/verify/jwt_module_{}'.format(self._transit_mount_point, module_name): {
                        'capabilities': ['create', 'update']
                    },
                    '{}/verify/jwt_module_{}/*'.format(self._transit_mount_point, module_name): {
                        'capabilities': ['create', 'update']
                    }
                }
            }

        self._client.sys.create_or_update_policy(
            name='{}modules_{}'.format(self._policy_prefix, module_name),
            policy=module_policy,
        )

    def _create_module_entity(self, module, extra_data=None, module_name=None):
        """
            Create or update Vault entity and policies for a given module

            :param module: Module description tuple
            :type module: dict
            :param extra_data: Additional arguments to add to entity metadata
            :type extra_data: dict
            :param module_name: Name for the new module. If not provided the name in the module is used.
            :type module_name: str
        """

        # Set the module name
        if module_name is None:
            module_name = module['module']

        # Create the module policy
        self._create_module_policy(module_name)

        # Build configuration map and required policies
        config, policies = self._build_config_and_policies(module)

        # Create the metadata
        entity_metadata = {
            'module': module_name,
            'description': module['description'],
            'config': 'modules/{}/config'.format(module_name),
            'apps': 'modules/{}/apps'.format(module_name),
            'services': 'modules/{}/services'.format(module_name),
            'domain': '{}.{}'.format(module_name, self._config.get('TESLA_DOMAIN')),
        }

        # Add queues in case they are available
        if 'queues' in module['deployment']:
            entity_metadata['queues'] = ','.join(module['deployment']['queues'])

        # Add extra data
        if extra_data is not None:
            for data_key in extra_data:
                entity_metadata[data_key] = extra_data[data_key]

        # Write entity configuration keys
        self._client.secrets.kv.v2.create_or_update_secret(
            path='modules/{}/metadata'.format(module_name),
            secret={'data': entity_metadata},
            mount_point=self._kv_mount_point
        )
        self._client.secrets.kv.v2.create_or_update_secret(
            path='modules/{}/config'.format(module_name),
            secret={'data': list(config)},
            mount_point=self._kv_mount_point
        )
        self._client.secrets.kv.v2.create_or_update_secret(
            path='modules/{}/apps'.format(module_name),
            secret={'data': module['apps']},
            mount_point=self._kv_mount_point
        )
        self._client.secrets.kv.v2.create_or_update_secret(
            path='modules/{}/services'.format(module_name),
            secret={'data': module['services']},
            mount_point=self._kv_mount_point
        )

        # Create a role for this module
        self._client.auth.approle.create_or_update_approle(
            module_name,
            mount_point=self._approle_mount_point,
            token_policies=list(policies)
        )

        # Create Celery credentials for all modules
        # TODO: Use per module credentials
        if 'celery' in module['services']:
            prefix = module_name
            if module['module'].startswith('provider'):
                prefix = 'provider'
            self._client.secrets.kv.v2.create_or_update_secret(
                path='config/celery/credentials/{}_user'.format(prefix),
                secret={
                    'description': 'User to authenticate with broker',
                    'value': self._config.get('CELERY_BROKER_USER')
                },
                mount_point=self._kv_mount_point
            )
            self._client.secrets.kv.v2.create_or_update_secret(
                path='config/celery/credentials/{}_password'.format(prefix),
                secret={
                    'description': 'Password to authenticate with broker',
                    'value': self._config.get('CELERY_BROKER_PASSWORD')
                },
                mount_point=self._kv_mount_point
            )

    def _update_configuration(self):
        """
            Update general configuration on KV store
        """
        # Get current configuration
        try:
            tesla_config = self._client.secrets.kv.v2.read_secret_version(path='config/public/config',
                                                                          mount_point=self._kv_mount_point
                                                                          )['data']['data']
        except InvalidPath:
            tesla_config = {}

        # Update with new configuration values
        tesla_config['TESLA_DOMAIN'] = self._config.get('TESLA_DOMAIN')

        self._client.secrets.kv.v2.create_or_update_secret(
            path='config/public/config',
            secret=dict(tesla_config),
            mount_point=self._kv_mount_point
        )

    def register_vle(self, vle):
        """
            Register a new VLE on vault or update current information

            :param vle: VLE model instance
            :type vle: tesla_ce.models.VLE
        """
        vle_template = get_vle_properties()
        module_name = 'vle_{}'.format(str(vle.id).zfill(3))
        vle_template['module'] = module_name
        extra_data = {
            'vle_name': vle.name,
            'vle_id': vle.id,
            'vle_url': vle.url,
            'institution_acronym': vle.institution.acronym,
            'institution_id': vle.institution.id
        }

        self._create_module_entity(vle_template, extra_data, module_name)

        self._create_jwt_key(MODULE_KEY_STR_TEMPLATE.format(module_name))

        return module_name

    def register_provider(self, provider):
        """
            Register a new Provider on vault or update current information

            :param provider: Provider model instance
            :type provider: tesla_ce.models.Provider
        """
        provider_template = get_provider_properties()
        module_name = 'provider_{}'.format(str(provider.id).zfill(3))
        provider_template['module'] = module_name
        extra_data = {
            'provider_name': provider.name,
            'provider_id': provider.id,
            'provider_acronym': provider.acronym,
            'provider_queue': provider.queue,
            'instrument_id': provider.instrument.id
        }

        self._create_module_entity(provider_template, extra_data, module_name)

        self._create_jwt_key(MODULE_KEY_STR_TEMPLATE.format(module_name))

        return module_name
