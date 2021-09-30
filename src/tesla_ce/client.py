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
""" TeSLA Client module"""
import json
import os
import uuid

import simplejson
from cache_memoize import cache_memoize
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils import timezone

from . import models
from .lib import ConfigManager
from .lib import DatabaseManager
from .lib import DeploymentManager
from .lib import StorageManager
from .lib import VaultManager
from .lib.checks import check_db_configuration
from .lib.checks import check_tesla_configuration
from .lib.checks import check_vault_configuration
from .lib.decorators import tesla_mode_required
from .lib.exception import TeslaAuthException
from .lib.exception import TeslaConfigException
from .lib.exception import TeslaInvalidICException
from .lib.exception import TeslaMissingEnrolmentException
from .lib.exception import TeslaMissingICException
from .lib.exception import TeslaVaultException

#: Client instance
_client = None


def get_version():
    """
        Get current version
        :return: Version value
    """
    version_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib', 'data', 'VERSION'))
    with open(version_file, 'r') as v_file:
        version = v_file.read()
    version = version.strip()
    return version


def get_default_client():
    """
        Get a client instance

        :return: Client instance
        :rtype: Client
    """
    global _client

    if _client is not None:
        return _client
    if not hasattr(settings, 'TESLA_CONFIG'):
        raise TeslaConfigException('Missing TeSLA configuration.')
    if len(settings.TESLA_CONFIG.enabled_modules) == 0:
        raise TeslaConfigException('No module is active.')

    # Get the most appropriated configuration
    config = None
    if len(settings.TESLA_CONFIG.enabled_modules) == 1:
        config = settings.TESLA_CONFIG.get_module_config(settings.TESLA_CONFIG.enabled_modules[0])
    elif 'api' in settings.TESLA_CONFIG.enabled_modules:
        config = settings.TESLA_CONFIG.get_module_config('api')
    elif 'lapi' in settings.TESLA_CONFIG.enabled_modules:
        config = settings.TESLA_CONFIG.get_module_config('lapi')
    else:
        config = settings.TESLA_CONFIG.get_module_config(settings.TESLA_CONFIG.enabled_modules[0])

    # Create the client instance
    _client = Client.create_instance(config['VAULT_URL'], config['VAULT_ROLE_ID'],
                                     config['VAULT_SECRET_ID'], config['VAULT_SSL_VERIFY'])
    return _client


class Client():
    """
        TeSLA Client, that provides a high level interface with the system

        :param config: Access to the configuration manager
        :type config: class:`tesla_ce.lib.config.ConfigManager`
        :param management_mode: Indicates whether the client is in management mode
        :type management_mode: bool
    """
    # Client version
    version = get_version()

    @staticmethod
    def create_instance(vault_url, role_id, secret_id, verify_ssl=True, approle_path=None, kv_path=None):
        """
            Create a client instance from Vault configuration

            :param vault_url: Url to connect with Vault.
            :type vault_url: str
            :param role_id: RoleID value.
            :type role_id: str
            :param secret_id: SecretID value.
            :type secret_id: str
            :param verify_ssl: Verify Vault certificate
            :type verify_ssl: bool
            :param approle_path: Mount point for AppRole authentication service
            :type approle_path: str
            :param kv_path: Mount point for KV secrets service
            :type kv_path: str
            :return: Client instance
            :rtype: Client
        """
        config = ConfigManager(load_config=False)
        config.config.set('VAULT_SSL_VERIFY', verify_ssl)
        config.load_vault(vault_url=vault_url, role_id=role_id, secret_id=secret_id,
                          kv_path=kv_path, approle_path=approle_path)
        return Client(config=config)

    def __init__(self, config=None, config_file=None, use_vault=True, use_env=True, enable_management=False):
        """
            Default constructor from configuration options

            :param config_file: Configuration file
            :type config_file: str
            :param use_vault: User vault to retrieve configuration values
            :type use_vault: bool
            :param use_env: User environment variables and secrets
            :type use_env: bool
            :param enable_management: Client created in management mode, used for administration purposes
            :type enable_management: bool

        """
        self._db = None
        self._vault = None
        self._deploy = None
        self._storage = None
        if config is None:
            config = ConfigManager(use_env=use_env, use_vault=use_vault, config_file=config_file)

        # Create a manager for Vault
        self._create_from_object(config, enable_management)

    def _create_from_object(self, config, enable_management=False):
        """
            Auxiliary method for object constructor

            :param config: Configuration manager object
            :type config: tesla_ce.lib.ConfigManager
            :param enable_management: Client created in management mode, used for administration purposes
            :type enable_management: bool

        """
        self._config = config
        self.management_mode = enable_management
        self._config.config.set('VAULT_MANAGEMENT', enable_management)

        # Only connect managers when running in production mode
        if self._config.config.get('TESLA_MODE') == 'production':
            # Create a manager for Vault
            self._vault = VaultManager(self.config)

            # Create a manager for the database
            self._db = DatabaseManager(self.config)

            # Create a manager for storage
            self._storage = StorageManager(self.config)

        # Create the deployment manager
        self._deploy = DeploymentManager(self)

    @property
    def vault(self):
        """
            Access to the HashiCorp Vault manager
            :return: Instance of the Vault manager
        """
        if self._vault is None:
            self._vault = VaultManager(self.config)
        return self._vault

    @property
    def database(self):
        """
            Access to the database manager
            :return: Instance of the database manager
        """
        if self._db is None:
            self._db = DatabaseManager(self.config)
        return self._db

    @property
    def config(self):
        """
            Access to the configuration manager
            :return: Instance of the configuration manager
        """
        return self._config

    @property
    def deploy(self):
        """
            Access to the deployment manager
            :return: Instance of the deployment manager
        """
        return self._deploy

    @property
    def storage(self):
        """
            Access to the storage manager
            :return: Instance of the storage manager
        """
        return self._storage

    @classmethod
    @tesla_mode_required('config')
    def generate_configuration(cls, output_file, domain, deploy_external_services=False, deploy_moodle=False):
        """
            Generates a configuration file with all the options

            :param output_file: File where configuration will be stored
            :type output_file: str
            :param domain: Base domain that will be used for TeSLA
            :type domain: str
            :param deploy_external_services: If enabled, external services configuration will be generated
            :type deploy_external_services: bool
            :param deploy_moodle: If enabled, moodle configuration will be generated
            :type deploy_moodle: bool
        """
        # Create an empty configuration object
        conf_manager = ConfigManager(load_config=False)

        # Load configuration from environment variables and secrets
        conf_manager.load_env()

        # Load from current file
        if os.path.exists(output_file):
            conf_manager.load_file(output_file)

        # Use this as base configuration
        config = conf_manager.config

        # Store domain information
        config.set('TESLA_DOMAIN', domain)

        # Generate a mail for admin
        config.set('TESLA_ADMIN_MAIL', 'admin@{}'.format(domain))

        # Generate DJango configuration
        config.set('DJANGO_SECRET_KEY', uuid.uuid4().__str__())
        config.set('DJANGO_ALLOWED_HOSTS', domain)

        # If external services are included, generate credentials and configuration
        if deploy_external_services:
            # Enable the services flag
            config.set('DEPLOYMENT_SERVICES', True)

            # Generate TeSLA Database configuration
            config.set('DB_HOST', 'database')
            config.set('DB_NAME', 'tesla')
            config.set('DB_USER', 'tesla')
            config.set('DB_ROOT_PASSWORD', uuid.uuid4().__str__())
            config.set('DB_PASSWORD', uuid.uuid4().__str__())

            # Generate Vault configuration
            config.set('VAULT_URL', 'https://vault.{}'.format(domain))
            config.set('VAULT_DB_HOST', 'database')
            config.set('VAULT_DB_NAME', 'vault')
            config.set('VAULT_DB_USER', 'vault')
            config.set('VAULT_DB_PASSWORD', uuid.uuid4().__str__())

            # Generate Redis configuration
            config.set('REDIS_HOST', 'redis')
            config.set('REDIS_PASSWORD', uuid.uuid4().__str__())

            # Generate MinIO configuration
            config.set('STORAGE_URL', 'https://storage.{}'.format(domain))
            config.set('STORAGE_ACCESS_KEY', uuid.uuid4().__str__())
            config.set('STORAGE_SECRET_KEY', uuid.uuid4().__str__())

            # Generate RabbitMQ configuration
            config.set('RABBITMQ_ERLANG_COOKIE', uuid.uuid4().__str__())
            config.set('RABBITMQ_ADMIN_USER', uuid.uuid4().__str__())
            config.set('RABBITMQ_ADMIN_PASSWORD', uuid.uuid4().__str__())

            # Generate Celery configuration
            config.set('CELERY_BROKER_HOST', 'rabbitmq')
            config.set('CELERY_BROKER_PORT', config.get('RABBITMQ_PORT'))
            config.set('CELERY_BROKER_USER', config.get('RABBITMQ_ADMIN_USER'))
            config.set('CELERY_BROKER_PASSWORD', config.get('RABBITMQ_ADMIN_PASSWORD'))

        # If Moodle is included, generate credentials and configuration
        if deploy_moodle:
            # Enable the moodle flag
            config.set('MOODLE_DEPLOY', True)

            # Generate Moodle Database configuration
            config.set('MOODLE_DB_HOST', config.get('DB_HOST'))
            config.set('MOODLE_DB_PASSWORD', uuid.uuid4().__str__())

            # Generate Moodle administrator password
            config.set('MOODLE_ADMIN_PASSWORD', uuid.uuid4().__str__())

        # Write the configuration file to disk
        with open(output_file, 'w') as out_fh:
            config.write(out_fh)

    def check_configuration(self):
        """
            Check the current configuration

            :return: Report of the configuration check
            :rtype: dict
        """
        storage_status = self.storage.get_status()
        storage_report = {
            'valid': storage_status['status'] == 1,
            'errors': storage_status['info']['errors'],
        }
        report = {
            'tesla': check_tesla_configuration(self.config.config),
            'database': check_db_configuration(self.config.config),
            'vault': check_vault_configuration(self.config.config),
            'storage': storage_report,
        }
        valid = True
        for service in report:
            if not report[service]['valid']:
                valid = False
                break
        report['valid'] = valid

        return report

    @tesla_mode_required('config')
    def initialize(self):
        """
            Initialize the TeSLA CE instance

            :exception TeslaAuthException: If management mode is not enabled
        """
        # Check management mode
        if not self.management_mode:
            raise TeslaAuthException('This operation requires enabled management mode')

        # Check configuration
        report = self.check_configuration()
        if not report['valid']:
            raise TeslaConfigException('Invalid configuration')

        # Initialize Vault
        self.vault.initialize()

        # Initialize the database
        self.database.initialize()

        # Initialize the storage
        self.storage.initialize()

    def get_learner_token_pair(self, learner, scope, filters=None, ttl=15, max_ttl=120):
        """
            Get a JWT token pair for a given learner

            :param leraner: Learner object
            :type learner: tesla_ce.models.Learner
            :param scope: List of tasks allowed for this token
            :type scope: list
            :param filters: Dictionary with the filters applied to the scope
            :type filters: dict
            :param ttl: Time to live for the token in minutes
            :type ttl: int
            :param max_ttl: Maximum time this token can be refreshed
            :type max_ttl: int

            :return: JWT token pair for this learner
            :rtype: dict
        """
        data = {
            'sub': learner.learner_id.__str__(),
            'type': 'learner',
            'pk': learner.id,
            'scope': scope,
            'filters': filters
        }

        return self.vault.create_token_pair(data, ttl=ttl, max_ttl=max_ttl, key='learners')

    def refresh_token(self, access_token, refresh_token):
        """
            Refresh given token.

            :param access_token: The JWT token to be refreshed
            :type access_token: str
            :param refresh_token: The JWT refresh token authenticating this operation
            :type refresh_token: str
            :return: JWT token
            :rtype: str
        """
        try:
            return self.vault.refresh_token(access_token, refresh_token)
        except TeslaVaultException:
            raise TeslaAuthException('Token refresh not authorized')

    def get_user_token_pair(self, user, scope, filters=None, ttl=15, max_ttl=120):
        """
            Get a JWT token pair for a given user

            :param user: Institution user object
            :type user: tesla_ce.models.InstitutionUser
            :param scope: List of tasks allowed for this token
            :type scope: list
            :param filters: Dictionary with the filters applied to the scope
            :type filters: dict
            :param ttl: Time to live for the token in minutes
            :type ttl: int
            :param max_ttl: Maximum time this token can be refreshed
            :type max_ttl: int

            :return: JWT token pair for this user
            :rtype dict
        """
        data = {
            'sub': user.uid,
            'type': 'user',
            'pk': user.id,
            'scope': scope,
            'filters': filters
        }

        return self.vault.create_token_pair(data, ttl=ttl, max_ttl=max_ttl, key='users')

    def get_admin_token_pair(self, user, scope, filters=None, ttl=15, max_ttl=120):
        """
            Get a JWT token pair for a given user

            :param user: User object
            :type user: tesla_ce.models.User
            :param scope: List of tasks allowed for this token
            :type scope: list
            :param filters: Dictionary with the filters applied to the scope
            :type filters: dict
            :param ttl: Time to live for the token in minutes
            :type ttl: int
            :param max_ttl: Maximum time this token can be refreshed
            :type max_ttl: int

            :return: JWT token pair for this user
            :rtype dict
        """
        if not user.is_staff:
            raise TeslaAuthException('User is not admin')
        data = {
            'sub': user.username,
            'type': 'admin',
            'pk': user.id,
            'scope': scope,
            'filters': filters
        }

        return self.vault.create_token_pair(data, ttl=ttl, max_ttl=max_ttl, key='users')

    def get_instructor_token(self, mail, scope, filters=None, ttl=60):
        """
            Get a JWT token for an instructor

            :param mail: Instructor email
            :type mail: str
            :param scope: List of tasks allowed for this token
            :type scope: list
            :param filters: Dictionary with the filters applied to the scope
            :type filters: dict
            :param ttl: Time to live for the token in minutes
            :type ttl: int

            :return: JWT token for this instructor
        """
        data = {
            'sub': mail,
        }

        return self.vault.create_token(data, ttl=ttl, key='instructors')

    def get_module_token(self, scope, module_id=None, filters=None, ttl=60, data=None):
        """
            Get a JWT token for a module

            :param module_id: Module unique identifier
            :type module_id: str
            :param scope: List of tasks allowed for this token
            :type scope: list
            :param filters: Dictionary with the filters applied to the scope
            :type filters: dict
            :param ttl: Time to live for the token in minutes
            :type ttl: int
            :param data: Information to add on the payload of the token
            :type data: dict
            :return: JWT token for this module
        """
        if module_id is None:
            module_info = self.config.get_module()
            module_id = module_info['module']
        if data is None:
            data = {}
        # Ensure required module information
        if module_id.startswith('provider_') or module_id.startswith('vle_'):
            id_parts = module_id.split('_')
            if 'type' not in data:
                data['type'] = id_parts[0]
            if 'pk' not in data:
                data['pk'] = int(id_parts[1])
        data['sub'] = module_id
        data['scope'] = scope
        data['filters'] = filters

        return self.vault.create_token(data, ttl=ttl, key='module_{}'.format(module_id))

    @cache_memoize(60 * 15)
    def validate_token(self, token):
        """
            Validate a token and return its data

            :param token: The token to be validated
            :type token: str
            :return: Token data
            :rtype: dict
            :exception TeslaAuthException: In case the token is invalid or expired
        """
        try:
            validation = self.vault.validate_token(token)
        except TeslaVaultException:
            raise TeslaAuthException('Invalid JWT token')

        if validation['valid']:
            return validation['payload']

        raise TeslaAuthException('Invalid JWT token')

    def verify_user(self, email, password):
        """
            Validate user credentials

            :param email: The user email
            :type email: str
            :param password: The user password
            :type password: str
            :return: User entity data
            :rtype: dict
            :exception TeslaAuthException: In case the credentials are not valid
        """
        try:
            user_info = self.vault.verify_user_password(email, password)
            user = models.User.objects.get(email=user_info['email'])
        except TeslaVaultException:
            raise TeslaAuthException('Invalid user credentials')
        except models.User.DoesNotExist:
            raise TeslaAuthException('Invalid user credentials')

        if user.is_staff:
            token_pair = self.get_admin_token_pair(user=user,
                                                   scope=['/api/v2/admin/*', '/api/v2/institution/*'],
                                                   max_ttl=60)
        elif hasattr(user, 'institutionuser'):
            inst_user = user.institutionuser
            scopes = ['/api/v2/institution/{}/user/{}/*'.format(
                inst_user.institution_id, inst_user.id
            )]
            if inst_user.inst_admin:
                scopes.append('/api/v2/institution/{}/*'.format(
                    inst_user.institution_id
                ))
            if inst_user.send_admin:
                scopes.append('/api/v2/institution/{}/send/*'.format(
                    inst_user.institution_id
                ))
            if inst_user.legal_admin:
                scopes.append('/api/v2/institution/{}/ic/*'.format(
                    inst_user.institution_id
                ))
            if 'LEARNER' in models.user.get_institution_roles(user):
                learner_id = str(inst_user.learner.learner_id)
                scopes.append('/lapi/v1/enrolment/{}/{}/'.format(
                    inst_user.institution_id,
                    learner_id
                ))
                scopes.append('/lapi/v1/status/{}/{}/'.format(
                    inst_user.institution_id,
                    learner_id
                ))
                scopes.append('/lapi/v1/alert/{}/{}/'.format(
                    inst_user.institution_id,
                    learner_id
                ))
                scopes.append('/api/v2/institution/{}/learner/{}/*'.format(
                    inst_user.institution_id, inst_user.id
                ))
            token_pair = self.get_user_token_pair(user=inst_user, scope=scopes, ttl=15, max_ttl=24*60)
        else:
            raise TeslaAuthException('Invalid user. Missing Institution or administration rights.')

        return token_pair

    def get_system_status(self):
        """
            Get the system status

            :return: Object with overall status and specific status for each module
            :rtype: dict
        """
        report = {
            'db': self.database.get_status(),
            'vault': self.vault.get_status(),
            'config': self.config.get_status(),
            'storage': self.storage.get_status(),
        }

        # Compute summary
        status = 1
        errors = 0
        warnings = 0
        for module in report:
            if report[module]['status'] == 0:
                status = 0
            errors += report[module]['errors']
            warnings += report[module]['warnings']

        return {
            'status': status,
            'warnings': warnings,
            'errors': errors,
            'info': {},
            'report': report
        }

    def export_deployment_scripts(self, output, mode=None):
        """
            Generates the files required to deploy TeSLA CE on a certain docker orchestrator

            :param output: Path to the folder where the scripts will be written
            :type output: str
            :param mode: The deployment mode (orchestrator) to be used
            :type mode: str
        """
        # Get the orchestrator
        if mode is None:
            mode = self.config.config.get('DEPLOYMENT_ORCHESTRATOR')

        files = self.deploy.get_deployment_scripts(mode)

        # Write files to disk
        if not os.path.exists(output):
            os.makedirs(output)
        for file in files:
            out_file = os.path.join(output, file)
            if not os.path.exists(os.path.dirname(out_file)):
                os.makedirs(os.path.dirname(out_file))
            with open(out_file, 'w') as out_fh:
                out_fh.write(files[file])

    def export_services_scripts(self, output, mode=None):
        """
            Generates the files required to deploy TeSLA CE required services on a certain docker orchestrator

            :param output: Path to the folder where the scripts will be written
            :type output: str
            :param mode: The deployment mode (orchestrator) to be used
            :type mode: str
        """
        # Get the orchestrator
        if mode is None:
            mode = self.config.config.get('DEPLOYMENT_ORCHESTRATOR')

        files = self.deploy.get_services_deployment_scripts(mode)

        # Write files to disk
        if not os.path.exists(output):
            os.makedirs(output)
        for file in files:
            out_file = os.path.join(output, file)
            if not os.path.exists(os.path.dirname(out_file)):
                os.makedirs(os.path.dirname(out_file))
            with open(out_file, 'w') as out_fh:
                out_fh.write(files[file])

    def export_vle_scripts(self, type, client_id, output, mode=None):
        """
            Generates the files required to deploy TeSLA CE VLE on a certain docker orchestrator

            :param type: Type of VLE. Accepted values are: 'moodle'
            :type type: str
            :param client_id: LTI 1.3 Client ID for this VLE
            :type client_id: str
            :param output: Path to the folder where the scripts will be written
            :type output: str
            :param mode: The deployment mode (orchestrator) to be used
            :type mode: str
        """
        # Get the orchestrator
        if mode is None:
            mode = self.config.config.get('DEPLOYMENT_ORCHESTRATOR')

        # Check the VLE type
        type_id = models.vle.get_type_id(type)
        if type_id is None:
            raise TeslaConfigException('Invalid VLE type')

        name = self.config.config.get('{}_NAME'.format(type.upper()))
        deploy = self.config.config.get('{}_DEPLOY'.format(type.upper()))
        if not deploy:
            raise TeslaConfigException('This VLE is not configured to be deployed')

        # Create the database and the user
        self.database.create_database(self.config.config.get('MOODLE_DB_NAME'))
        self.database.create_user(self.config.config.get('MOODLE_DB_NAME'),
                                  self.config.config.get('MOODLE_DB_USER'),
                                  self.config.config.get('MOODLE_DB_PASSWORD'))

        # Find VLE
        try:
            vle = models.VLE.objects.get(name=name)
        except models.VLE.DoesNotExist:
            institution = models.Institution.objects.first()
            vle = models.VLE.objects.create(name=name, type=type_id, url="", institution=institution,
                                            client_id=client_id)
            vle.save()
        files = self.deploy.get_vle_deployment_scripts(vle, mode)

        # Write files to disk
        if not os.path.exists(output):
            os.makedirs(output)
        for file in files:
            out_file = os.path.join(output, file)
            if not os.path.exists(os.path.dirname(out_file)):
                os.makedirs(os.path.dirname(out_file))
            with open(out_file, 'w') as out_fh:
                out_fh.write(files[file])

    def create_assessment_session(self, activity, learner, locale=None, max_ttl=120, redirect_reject_url=None,
                                  reject_message=None, options=None):
        """
            Create a new assessment session for a given activity and learner

            :param activity: The activity for the assessment session
            :type activity: tesla_ce.models.Activity
            :param learner: The learner for the assessment session
            :type learner: tesla_ce.models.Learner
            :param locale: Fix the locale to use for this assessment
            :type locale: str
            :param max_ttl: The maximum validity of provided tokens in minutes
            :type max_ttl: int
            :param redirect_reject_url: Redirect URL where learner is redirected if ethical warning is rejected
            :type redirect_reject_url: str
            :param reject_message: Message provided to learner in case ethical warning is rejected
            :type reject_message: str
            :param options: Options that can be passed to the data object to modify some default properties
            :return: Created session
            :rtype: tesla_ce.models.AssessmentSession
        """
        # Check learner informed consent status
        if not learner.institution.external_ic:
            if learner.consent_accepted is None or learner.consent_rejected is not None:
                raise TeslaMissingICException()

            if not learner.ic_status.startswith('VALID'):
                raise TeslaInvalidICException()

        # Get the list of instruments and enrolment values
        enrolment_obj = {
            'missing_enrolments': False,
            'instruments': {}
        }
        if activity.enabled:
            # Check enrolment status for this learner and activity
            enrolment_obj = learner.missing_enrolments(activity.id)
            if enrolment_obj['missing_enrolments']:
                raise TeslaMissingEnrolmentException(enrolment_obj)

        # Set the list of sensors
        activity_instruments = activity.get_learner_instruments(learner)
        sensors = {}
        instruments = []
        for instrument in activity_instruments:
            instruments.append(instrument.instrument_id)
            inst_sensor = instrument.get_sensors()
            for sensor in inst_sensor:
                if sensor not in sensors:
                    sensors[sensor] = []
                sensors[sensor].append(instrument.instrument_id)

        # Initialize a new Assessment Session
        session = models.AssessmentSession.objects.create(activity=activity, learner=learner)

        # Add the learner to the course
        activity.course.learners.add(learner)
        activity.course.save()

        # Get the learner token
        token = self.get_learner_token_pair(learner,
                                            [
                                                '/lapi/v1/verification/{}/{}/'.format(
                                                    learner.institution_id, learner.learner_id),
                                                '/lapi/v1/status/{}/{}/'.format(
                                                    learner.institution_id, learner.learner_id),
                                                '/lapi/v1/alert/{}/{}/'.format(
                                                    learner.institution_id, learner.learner_id)
                                            ], ttl=15, max_ttl=max_ttl,
                                            filters={
                                                "session_id": session.id,
                                                "mode": "verification"
                                            })

        # Create a Dashboard launcher
        launcher = self.get_launcher_token('dashboard', learner.institutionuser, session)

        # Compute the base path for assets
        base_url = '{}'.format(static('web-plugin/web-plugin.js').split('web-plugin.js')[0])

        # Set default options
        if options is None:
            options = {}
        if 'floating_menu_initial_pos' not in options:
            options['floating_menu_initial_pos'] = 'top-right'

        # Update the information
        session_connector_data = {
            'mode': 'verification',
            'learner': {
                'id': learner.id,
                'learner_id': learner.learner_id.__str__(),
                'first_name': learner.first_name,
                'last_name': learner.last_name,
                'picture': None,
                'institution_id': learner.institution_id,
            },
            'session_id': session.id,
            'activity': {
                'enabled': activity.enabled,
                'course': {
                    'id': activity.course.id,
                    'code': activity.course.code,
                    'description': activity.course.description,
                    'start': activity.course.start.isoformat() if activity.course.start is not None else None,
                    'end': activity.course.end.isoformat() if activity.course.end is not None else None,
                },
                'id': activity.id,
                'name': activity.name,
                'description': activity.description,
                'start': activity.start.isoformat() if activity.start is not None else None,
                'end': activity.end.isoformat() if activity.end is not None else None,
                'allow_reject_capture': False,
                'redirect_reject_url': redirect_reject_url,
                'rejected_message': reject_message,
                'vle_id': activity.vle_id,
            },
            'accessibility': {
                'high_contrast': False,
                'big_fonts': False,
                'text_to_speech': False
            },
            'instruments': instruments,
            'sensors': sensors,
            'token': token,
            'enrolment': enrolment_obj,
            'logo_url': static('img/android-chrome-192x192.png'),
            'api_url': settings.API_URL,
            'dashboard_url': settings.DASHBOARD_URL,
            'launcher': launcher,
            'base_url': base_url,
            'locale': locale,
            'options': options
        }

        # Store the session data
        session_data = models.AssessmentSessionData.objects.create(session=session)
        session_connector_data_path = os.path.join(str(learner.institution.id),
                                                   str(learner.learner_id),
                                                   'sessions',
                                                   str(session.activity_id),
                                                   str(session.id), 'data.json'
                                                   )
        session_data.data.save(session_connector_data_path,
                               ContentFile(simplejson.dumps(session_connector_data).encode('utf-8')))

        # Generate the connector
        connector_data = {
            'data_url': session_data.data.url,
            'modules': [
                static('web-plugin/web-plugin.js'),
            ],
            'css': [
                static('web-plugin/styles.css'),
            ],
            'active': activity.enabled and len(instruments) > 0
        }
        session_connector = render_to_string('web-plugin/connector.js',
                                             {'session_data': simplejson.dumps(connector_data)})

        # Create the data path
        session_connector_path = os.path.join(str(learner.institution.id),
                                              str(learner.learner_id),
                                              'sessions',
                                              str(session.activity_id),
                                              str(session.id), 'connector.js'
                                    )
        # Write assessment info file
        session_data.connector.save(session_connector_path, ContentFile(session_connector.encode('utf-8')))
        session_data.save()

        return session

    def register_vle(self, type, name, url=None, institution_acronym=None, client_id=None, force_update=False):
        """
            Register a new VLE to the system

            :param type: Type of VLE. Accepted values are: 'moodle'
            :type type: str
            :param name: Unique name for the VLE
            :type name: str
            :param url: URL of the VLE
            :type url: str
            :param institution_acronym: Acronym of the institution whit VLE belongs to
            :type institution_acronym: str
            :param client_id: LTI 1.3 Client ID for this VLE
            :type client_id: str
            :param force_update: If the VLE already exists, update the data
            :type force_update: bool
            :return: Configuration data for the new VLE
            :rtype: dict
        """
        # Check the institution
        if institution_acronym is not None:
            try:
                institution = models.Institution.objects.get(acronym=institution_acronym)
            except models.Institution.DoesNotExist:
                raise TeslaConfigException('Invalid institution acronym {}'.format(institution_acronym))
        else:
            if models.Institution.objects.count() > 1:
                raise TeslaConfigException('Multiple registered institutions. Institution acronym is required')
            institution = models.Institution.objects.first()

        # Check the VLE type
        type_id = models.vle.get_type_id(type)
        if type_id is None:
            raise TeslaConfigException('Invalid VLE type')

        # Create the register on the database
        try:
            vle = models.VLE.objects.get(name=name)
            if vle is not None and not force_update:
                raise TeslaConfigException(
                    'A VLE with this name already exist. User force_update to update current vle information'
                )
        except models.VLE.DoesNotExist:
            vle = models.VLE.objects.create(name=name, type=type_id, url=url, institution=institution,
                                            client_id=client_id)
            vle.save()

        # Update LTI data
        if vle.lti is None:
            lti = {}
        else:
            lti = json.loads(vle.lti)

        # LTI 1.1 data
        if 'consumer_key' not in lti or lti['consumer_key'] is None or len(lti['consumer_key']) == 0:
            lti['consumer_key'] = uuid.uuid4().__str__()
        if 'consumer_secret' not in lti or lti['consumer_secret'] is None or len(lti['consumer_secret']) == 0:
            lti['consumer_secret'] = uuid.uuid4().__str__()

        # LTI 1.3 data
        # Update URLs for known VLEs
        if url is not None and type.upper() == 'MOODLE':
            lti['auth_login_url'] = '{}/mod/lti/auth.php'.format(url)
            lti['auth_token_url'] = '{}/mod/lti/token.php'.format(url)
            lti['key_set_url'] = '{}/mod/lti/certs.php'.format(url)

        # Update the VLE object
        vle.lti = json.dumps(lti)
        vle.save()

        # Register the vle
        vle_info = self.vault.register_vle(vle)
        vle_info.update(lti)

        # Add API URL
        vle_info['api_url'] = 'https://{}'.format(self.config.config.get('TESLA_DOMAIN'))

        return vle_info

    def register_provider(self, provider_info, force_update=False):
        """
            Register a new Provider to the system

            :param provider_info: Provider information. Should be provided by the provider
            :type provider_info: dict
            :param force_update: If the Provider already exists, update the data
            :type force_update: bool
            :return: Configuration data for the new Provider
            :rtype: dict
        """
        try:
            provider = models.Provider.objects.get(instrument_id=provider_info['instrument'],
                                                   acronym=provider_info['acronym'])
            provider.image = provider_info['image']
            provider.name = provider_info['name']
            provider.version = provider_info['version']
            provider.queue = provider_info['queue']
            provider.url = provider_info.get('url'),
            provider.description = provider_info['description']
            provider.has_service = provider_info.get('has_service', False)
            provider.service_port = provider_info.get('service_port')
            provider.options_schema = provider_info.get('options_schema')
            provider.allow_validation = provider_info.get('allow_validation', False)
            provider.alert_below = provider_info.get('alert_below')
            provider.warning_below = provider_info.get('warning_below')
            provider.inverted_polarity = provider_info.get('inverted_polarity', False)
            provider.save()
        except models.Provider.DoesNotExist:
            provider = models.Provider.objects.create(
                instrument_id=provider_info['instrument'],
                acronym=provider_info['acronym'],
                image=provider_info['image'],
                name=provider_info['name'],
                version = provider_info['version'],
                queue = provider_info['queue'],
                url=provider_info.get('url'),
                description=provider_info['description'],
                has_service=provider_info.get('has_service', False),
                service_port=provider_info.get('service_port'),
                options_schema=provider_info.get('options_schema'),
                allow_validation=provider_info.get('allow_validation', False),
                alert_below=provider_info.get('alert_below'),
                warning_below=provider_info.get('warning_below'),
                inverted_polarity=provider_info.get('inverted_polarity', False)
            )
        # Register the provider module
        prov_info = self.vault.register_provider(provider)
        return prov_info

    def get_launcher_token(self, target, user, session=None, target_url=None, ttl=None):
        """
            Create a launcher token

            :param target:
            :param user:
            :param session:
            :param target_url:
            :param ttl:
            :return: Launcher credentials
            :rtype: dict
        """
        target_id = None
        token_pair = None
        if target.upper() == 'DASHBOARD':
            target_id = 0
            if ttl is None:
                ttl = 24 * 60
            token_pair = self.get_user_token_pair(user=user, scope=['/api/v2/institution/{}/user/{}/*'.format(
                user.institution_id, user.id
            )], max_ttl=ttl)
        elif target.upper() == 'LAPI':
            target_id = 1
            if ttl is None:
                ttl = 2 * 60
            try:
                learner = user.learner
            except user.learner.RelatedObjectDoesNotExist:
                raise TeslaAuthException('Provided user is not a learner')
            token_pair = self.get_learner_token_pair(learner=learner, scope=['/lapi/*'], max_ttl=ttl)

        if target_id is None or token_pair is None:
            raise TeslaConfigException('Invalid target type')

        expiration = timezone.now() + timezone.timedelta(minutes=ttl)

        launcher =  models.Launcher.objects.create(user=user, token=uuid.uuid4(), session=session, target_url=target_url,
                                                   token_pair=token_pair, expires_at=expiration)

        return {
            'id': launcher.id,
            'token': launcher.token.__str__()
        }
