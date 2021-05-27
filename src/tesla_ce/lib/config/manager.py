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
#
""" Configuration Manager Module"""
import configparser
import os

import hvac
from hvac.exceptions import InvalidRequest

from .conf import Config
from ..checks import check_vault_connection
from ..exception import TeslaConfigException


class ConfigManager:
    """ Manager class for configuration

        Contains the utility methods to manage configuration
    """
    #: Default path for secrets
    secrets_path = '/run/secrets'

    #: Search paths for configuration
    search_path = ['./tesla-ce.cfg', '/etc/tesla/tesla-ce.cfg']

    def __init__(self, load_config=True, secrets_path='/run/secrets', use_env=True, use_vault=True, config_file=None):
        """
            Default constructor

            :param load_config: Load configuration from default sources
            :type load_config: bool
            :param secrets_path: Base path for secrets. Default /run/secrets
            :type secrets_path: str
            :param use_env: Load configuration from environment variables
            :type use_env: bool
            :param use_vault: Load configuration from HashiCorp Vault
            :type use_vault: bool
            :param config_file: File to load the configuration from. If provided, other options will be ignored.
            :type config_file: str
        """
        #: Configuration object where configuration is stored
        self.config = Config()

        # Set secrets path
        self.secrets_path = secrets_path

        # List of enabled modules
        self.enabled_modules = []

        # Modules data
        self.modules = {}

        # Load configuration
        if load_config:
            # If a file is not provided, search in standard locations
            if config_file is None:
                config_file = self.find_config_file()

            # Load the configuration
            self.load(use_env=use_env, use_vault=use_vault, file_path=config_file)

    @classmethod
    def find_config_file(cls):
        """
            Looks for configuration path in the list of search paths

            :return: Path to the configuration file or None if not found
        """
        for file in cls.search_path:
            if os.path.exists(os.path.abspath(file)):
                return os.path.abspath(file)
        return None

    def save_configuration(self):
        """
            Save current configuration to the configuration file
        """
        # Check if configuration has been loaded from a file
        config_file = self.config.get('TESLA_CONFIG_FILE')

        # If there is no file for the configuration, find the most appropriate path
        if config_file is None:
            # TODO: Try with /etc/tesla first
            config_file = 'tesla-ce.cfg'

        # Write configuration to disk
        with open(config_file, 'w') as conf_fh:
            self.config.write(conf_fh)
        # Change permissions to the file
        os.chmod(config_file, 0o600)

    def load(self, file_path=None, vault_role=None, vault_secret=None, vault_url=None, use_env=True, use_vault=True):
        """
            Load configuration options

            :param file_path: If provided, read options in file.
            :type file_path: str
            :param vault_role: Role value to connect to Vault. If provided value in environment variable is not used
            :type vault_role: str
            :param vault_secret: Secret value to connect to Vault. If provided value in environment variable is not used
            :type vault_secret: str
            :param vault_url: Full URL to connect with vault (ie. https://vault:8200)
            :type vault_url: str
            :param use_env: Load configuration from environment variables
            :type use_env: bool
            :param use_vault: Load configuration from HashiCorp Vault
            :type use_vault: bool
            :exception TeslaConfigException: If the provided options are invalid
        """
        if not use_env and file_path is None and (vault_role is None or vault_secret is None):
            raise TeslaConfigException("Environment based config is disabled and no alternative is provided")

        # If file is provided, load configuration from file
        if file_path is not None:
            # Load configuration from file
            self.load_file(file_path)

            # Store the configuration file
            self.config.set('TESLA_CONFIG_FILE', file_path)
        # Try to load configuration from system
        if use_env:
            # Load configuration from secrets and environment variables
            self.load_env()
        # Get configuration from Vault
        if use_vault:
            if vault_role is not None and vault_secret is not None:
                # Update authentication values for vault with provided ones
                self.config.set('VAULT_ROLE_ID', vault_role)
                self.config.set('VAULT_SECRET_ID', vault_secret)
            if vault_url is not None:
                self.config.set('VAULT_URL', vault_url)
            if self.config.get('VAULT_ROLE_ID') is not None and self.config.get('VAULT_SECRET_ID') is not None:
                self.load_vault()

    def load_file(self, path):
        """
            Load configuration options from file

            :param path: Absolute path to configuration file
            :type path: str
            :exception TeslaConfigException: If the provided file is not found or is incorrect
        """
        if path is not None:
            if os.path.exists(path):
                conf = configparser.ConfigParser()
                with open(path, 'r') as conf_file:
                    conf.read_file(conf_file, path)
                    self.config.update(conf)
            else:
                raise TeslaConfigException("Cannot find provided file: {}".format(path))

    @staticmethod
    def _get_vault_entity_data(role_id, secret_id, vault_url, verify_ssl=None,
                               approle_path='tesla-ce/approle', kv_path='tesla-ce/kv'):
        """
            Get entity data from Vault.

            :param role_id: RoleID value. If not provided, current configuration will be used to find this value
            :type role_id: str
            :param secret_id: SecretID value. If not provided, current configuration will be used to find this value
            :type secret_id: str
            :param vault_url: Url to connect with Vault. If not provided, current configuration will be used to find
                this value
            :type vault_url: str
            :exception TeslaConfigException: If the provided arguments are invalid or vault is not accessible
            :param verify_ssl: Indicates if the certificate provided by Valut should be verified and the CA
            :type verify_ssl: str | bool
            :param approle_path: Mount point for AppRole authentication service
            :type approle_path: str
            :param kv_path: Mount point for KV secrets service
            :type kv_path: str
            :return: Entity data from Vault
            :rtype: dict
        """
        # Load configuration for each credential
        client = hvac.Client(url=vault_url, verify=verify_ssl)
        try:
            auth_data = client.auth.approle.login(role_id, secret_id, mount_point=approle_path)
        except InvalidRequest:
            raise TeslaConfigException("Cannot authenticate with provided credentials")
        entity_data = client.secrets.kv.v2.read_secret_version(
            path='modules/{}/metadata'.format(auth_data['auth']['metadata']['role_name']),
            mount_point=kv_path
        )['data']['data']['data']

        conf = client.secrets.kv.v2.read_secret_version(path=entity_data['config'],
                                                        mount_point=kv_path)['data']['data']
        apps = client.secrets.kv.v2.read_secret_version(path=entity_data['apps'],
                                                        mount_point=kv_path)['data']['data']
        services = client.secrets.kv.v2.read_secret_version(path=entity_data['services'],
                                                            mount_point=kv_path)['data']['data']

        # Create the module description structure
        module = {
            'module': entity_data['module'],
            'description': entity_data['description'],
            'apps': apps['data'],
            'services': services['data'],
            'config': {
                'VAULT_URL': vault_url,
                'VAULT_ROLE_ID': role_id,
                'VAULT_SECRET_ID': secret_id,
                'VAULT_SSL_VERIFY': verify_ssl,
                'VAULT_MOUNT_PATH_APPROLE': approle_path,
                'VAULT_MOUNT_PATH_KV': kv_path
            },
            'queues': entity_data.get('queues')
        }

        # Add retrieved values
        for keypair in conf['data']:
            key = keypair[0]
            path = keypair[1]
            data = client.secrets.kv.v2.read_secret_version(path=path, mount_point=kv_path)['data']['data']
            value = data['value']
            module['config'][key] = value

        return module

    def load_vault(self, role_id=None, secret_id=None, vault_url=None, approle_path=None, kv_path=None):
        """
            Load configuration options from Hashicorp Vault

            :param role_id: RoleID value. If not provided, current configuration will be used to find this value
            :type role_id: str | list
            :param secret_id: SecretID value. If not provided, current configuration will be used to find this value
            :type secret_id: str | list
            :param vault_url: Url to connect with Vault. If not provided, current configuration will be used to find
                this value
            :type vault_url: str
            :param approle_path: Mount point for AppRole authentication service
            :type approle_path: str
            :param kv_path: Mount point for KV secrets service
            :type kv_path: str
            :exception TeslaConfigException: If the provided arguments are invalid or vault is not accessible
        """
        if role_id is None:
            role_id = self.config.get('VAULT_ROLE_ID')
        else:
            self.config.set('VAULT_ROLE_ID', role_id)
        if secret_id is None:
            secret_id = self.config.get('VAULT_SECRET_ID')
        else:
            self.config.set('VAULT_SECRET_ID', secret_id)
        if approle_path is None:
            approle_path = self.config.get('VAULT_MOUNT_PATH_APPROLE')
        else:
            self.config.set('VAULT_MOUNT_PATH_APPROLE', approle_path)
        if kv_path is None:
            kv_path = self.config.get('VAULT_MOUNT_PATH_KV')
        else:
            self.config.set('VAULT_MOUNT_PATH_KV', kv_path)
        if vault_url is None:
            vault_url = self.config.get('VAULT_URL')
        else:
            self.config.set('VAULT_URL', vault_url)
        verify_ssl = self.config.get('VAULT_SSL_VERIFY')

        # Check if required information is provided
        if role_id is None or secret_id is None or vault_url is None:
            # Skip configuration
            return

        # Check if vault is available
        vault_connection_report = check_vault_connection(config=self.config)
        if not vault_connection_report['ready']:
            if role_id is not None and secret_id is not None:
                # Starting as module. Abort if cannot connect to Vault
                raise TeslaConfigException('Cannot connect to Vault with provided credentials.')
            # Skip configuration, as we are in Configuration mode
            return

        # Check if multiple credentials are provided
        self.enabled_modules = []
        if isinstance(role_id, list):
            assert len(role_id) == len(secret_id)
        else:
            role_id = [role_id]
            secret_id = [secret_id]
        for idx, role in enumerate(role_id):
            module = self._get_vault_entity_data(role_id[idx], secret_id[idx], vault_url, verify_ssl=verify_ssl,
                                                 approle_path=approle_path, kv_path=kv_path)
            self.modules[module['module']] = module
            self.enabled_modules.append(module['module'])

        # Get configuration from all modules
        config = self._get_config()
        for key in config:
            self.config.set(key, config[key])

    def load_env(self):
        """
            Load configuration options from Docker Secrets and Environment variables
        """
        # Read values in secrets
        if os.path.exists(self.secrets_path):
            for secret in list(os.scandir(self.secrets_path)):
                if self.config.is_valid_key(secret.name):
                    with open(secret.path, 'r') as f_secret:
                        value = f_secret.read()
                        self.config.set(secret.name, value)

        # Read options from environment variables
        for k in os.environ.keys():
            if self.config.is_valid_key(k):
                self.config.set(k, os.getenv(k))
            elif k.upper().endswith('_FILE'):
                # Try to read from file
                key = k.upper().split('_FILE')[0]
                if os.path.exists(os.getenv(k)) and self.config.is_valid_key(key):
                    with open(os.getenv(k), 'r') as f_secret:
                        value = f_secret.read()
                        self.config.set(key, value)

    def get_module(self, module=None):
        """
            Get the module information

            :param module: Name of the module in case of multiple modules enabled
            :type module: str
            :return: Module information
            :rtype: dict
        """
        if self.modules is None or len(self.modules) == 0:
            raise TeslaConfigException('No module configuration available')

        if module is None and len(self.modules) > 1:
            raise TeslaConfigException('Multiple modules enabled. Module must be provided')

        if module is None:
            module = list(self.modules.keys())[0]

        if module in self.modules.keys():
            return self.modules[module]

        raise TeslaConfigException('No module configuration available for {}'.format(module))

    def get_module_config(self, module=None):
        """
            Get the module configuration

            :param module: Name of the module in case of multiple modules enabled
            :type module: str
            :return: Module configuration
            :rtype: dict
        """
        info = self.get_module(module)
        if 'config' in info:
            return info['config']

        raise TeslaConfigException('No module configuration available')

    def _get_config(self):
        """
            Get configuration object merging all available modules configurations

            :return: Module configuration
            :rtype: dict
        """
        has_api = False
        config = {}
        for module in self.modules:
            if module == 'api':
                has_api = True
                continue
            mod_config = self.get_module_config(module)
            config.update(mod_config)
        # API configuration have precedence. If api is one of the modules, apply it the end
        if has_api:
            api_config = self.get_module_config('api')
            config.update(api_config)

        return config

    def get_database_config(self):
        """
            Return database configurations

            :return: Database configurations
            :rtype: dict
        """
        db = {}
        has_db = False
        for module in self.modules:
            if self.modules[module].get('services') is not None and 'db' in self.modules[module].get('services'):
                has_db = True
                mod_config = self.get_module_config(module)
                db[module] = {
                    'ENGINE': 'django.db.backends.{}'.format(mod_config.get('DB_ENGINE')),
                    'HOST': mod_config.get('DB_HOST'),
                    'NAME': mod_config.get('DB_NAME'),
                    'USER': mod_config.get('DB_USER'),
                    'PASSWORD': mod_config.get('DB_PASSWORD'),
                    'PORT': mod_config.get('DB_PORT'),
                }
        if len(list(db.keys())) > 0:
            db['default'] = db[list(db.keys())[0]]
        if not has_db:
            db = {}
        return db

    def get_cache_config(self):
        """
            Return cache configuration

            :return: Cache configuration
            :rtype: dict
        """
        cache = {}
        has_cache = False
        for module in self.modules:
            if self.modules[module].get('services') is not None and 'redis' in self.modules[module].get('services'):
                has_cache = True
                mod_config = self.get_module_config(module)
                cache[module] = {
                    #'BACKEND': 'django_redis.cache.RedisCache',
                    'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',
                    'LOCATION': "redis://{}:{}/{}".format(mod_config.get('REDIS_HOST'),
                                                          mod_config.get('REDIS_PORT'),
                                                          mod_config.get('REDIS_DATABASE')),
                    'OPTIONS': {
                        'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                        'PASSWORD': mod_config.get('REDIS_PASSWORD')
                    }
                }
        if len(list(cache.keys())) > 0:
            cache['default'] = cache[list(cache.keys())[0]]
        if not has_cache:
            cache['default'] = {
                #'BACKEND': 'django_redis.cache.RedisCache',
                'BACKEND': 'django_prometheus.cache.backends.redis.RedisCache',
                'LOCATION': "redis://{}:{}/{}".format(self.config.get('REDIS_HOST'),
                                                      self.config.get('REDIS_PORT'),
                                                      self.config.get('REDIS_DATABASE')),
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'PASSWORD': self.config.get('REDIS_PASSWORD')
                }
            }
        return cache

    def get_celery_config(self):
        """
            Return celery broker url

            :return: Brocker url for each module
            :rtype: str
        """
        celery = {}
        has_celery = False
        for module in self.modules:
            if self.modules[module].get('services') is not None and 'celery' in self.modules[module].get('services'):
                has_celery = True
                mod_config = self.get_module_config(module)
                if mod_config.get('CELERY_BROKER_PROTOCOL') == 'sqs':
                    celery[module] = {
                        'CELERY_BROKER_TRANSPORT_OPTIONS': {'region': mod_config.get('CELERY_BROKER_REGION')},
                        'CELERY_BROKER_URL': '{0}://{1}:{2}@'.format(
                            'sqs',
                            mod_config.get('CELERY_BROKER_USER'),
                            mod_config.get('CELERY_BROKER_PASSWORD')
                        )
                    }
                else:
                    vhost = mod_config.get('CELERY_BROKER_VHOST')
                    if len(vhost) == 0 or vhost is None:
                        vhost = '/'
                    elif not vhost.startswith('/'):
                        vhost = '/' + vhost
                    celery[module] = {
                        'CELERY_BROKER_URL': '{}://{}:{}@{}:{}{}'.format(
                            mod_config.get('CELERY_BROKER_PROTOCOL'),
                            mod_config.get('CELERY_BROKER_USER'),
                            mod_config.get('CELERY_BROKER_PASSWORD'),
                            mod_config.get('CELERY_BROKER_HOST'),
                            mod_config.get('CELERY_BROKER_PORT'),
                            vhost
                        )
                    }

        if len(list(celery.keys())) > 0:
            if len(list(celery.keys())) > 1:
                if self.config.get('RABBITMQ_ADMIN_USER') is not None and \
                        self.config.get('RABBITMQ_ADMIN_PASSWORD') is not None:
                    celery = celery[list(celery.keys())[0]]['CELERY_BROKER_URL']
                    protocol = celery.split('//')[0]
                    host = celery.split('@')[1]
                    celery = '{}//{}:{}@{}'.format(protocol,
                                                   self.config.get('RABBITMQ_ADMIN_USER'),
                                                   self.config.get('RABBITMQ_ADMIN_PASSWORD'),
                                                   host
                                                   )
                else:
                    raise TeslaConfigException('Multiple celery configuration without administration credentials.')
            else:
                celery = celery[list(celery.keys())[0]]['CELERY_BROKER_URL']
        if not has_celery:
            # Use default parameters
            vhost = self.config.get('CELERY_BROKER_VHOST')
            if len(vhost) == 0 or vhost is None:
                vhost = '/'
            elif not vhost.startswith('/'):
                vhost = '/' + vhost
            celery = '{}://{}:{}@{}:{}{}'.format(
                        self.config.get('CELERY_BROKER_PROTOCOL'),
                        self.config.get('CELERY_BROKER_USER'),
                        self.config.get('CELERY_BROKER_PASSWORD'),
                        self.config.get('CELERY_BROKER_HOST'),
                        self.config.get('CELERY_BROKER_PORT'),
                        vhost
                    )

        return celery

    def get_status(self):
        """
            Get the configuration status

            :return: Object with status information
            :rtype: dict
        """
        return {
            'status': 0,
            'warnings': 0,
            'errors': 0,
            'info': {}
        }
