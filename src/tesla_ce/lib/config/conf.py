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
""" Configuration Module"""
import configparser

from ..exception import TeslaConfigException


class Config:
    """ Configuration class

        Allows to manage the configuration values and apply hierarchical configurations
    """
    #: Configuration sections
    _sections = (
        # (section_name, section_description, fields)
        #   (field_name, field_description, field_type, default, options, exportable)
        ('tesla', 'Generic configuration', (
            ('config_file', 'Configuration file to be used', 'str', None, None, False),
            ('mode', 'Working mode of TeSLA', 'enum', 'production', ['config', 'production', ], False),
            ('domain', 'Base domain', 'str', None, None, True),
            ('admin_mail', 'Mail of the administrator', 'str', None, None, True),
            ('institution_name', 'Name of the institution', 'str', 'Default Institution', None, True),
            ('institution_acronym', 'Acronym of the institution', 'str', 'default', None, True),
        )),
        ('db', 'Database configuration', (
            ('host', 'Database host', 'str', 'localhost', None, True),
            ('engine', 'Database engine', 'enum', 'mysql', ['mysql', 'postgresql',], True),
            ('port', 'Database port', 'int', 3306, None, True),
            ('name', 'Database name', 'str', 'tesla', None, True),
            ('user', 'Database user', 'str', None, None, True),
            ('password', 'Database password', 'str', None, None, True),
            ('root_user', 'Database root username', 'str', 'root', None, True),
            ('root_password', 'Database root password', 'str', None, None, True),
        )),
        ('vault', 'HashiCorp Vault configuration', (
            ('url', 'Vault complete URL', 'str', 'http://localhost:8200', None, True),
            ('ssl_verify', 'Verify SSL', 'bool', True, None, True),
            ('token', 'Token to authenticate', 'str', None, None, True),
            ('role_id', 'Role ID value to authenticate', 'list', None, None, False),
            ('secret_id', 'Secret ID value to authenticate', 'list', None, None, False),
            ('keys', 'Unseal keys for Vault', 'list', None, None, True),
            ('management', 'Allow Vault management', 'bool', False, None, False),
            ('db_host', 'MySQL host for vault database', 'str', None, None, True),
            ('db_port', 'MySQL port for vault database', 'int', 3306, None, True),
            ('db_name', 'MySQL database name for vault database', 'str', None, None, True),
            ('db_user', 'MySQL user for vault database', 'str', None, None, True),
            ('db_password', 'MySQL password for vault database', 'str', None, None, True),
            ('mount_path_kv', 'Mount path for KV secrets engine', 'str', 'tesla-ce/kv', None, True),
            ('mount_path_transit', 'Mount path for transit encryption engine', 'str', 'tesla-ce/transit', None, True),
            ('mount_path_approle', 'Mount path for approle auth engine', 'str', 'tesla-ce/approle', None, True),
            ('policies_prefix', 'Prefix prepended to ACL policy names', 'str', 'tesla-ce/policy/', None, True),
        )),
        ('redis', 'Redis configuration', (
            ('host', 'Redis host', 'str', 'localhost', None, True),
            ('port', 'Redis port', 'int', 6379, None, True),
            ('password', 'Redis password', 'str', None, None, True),
            ('database', 'Redis database', 'int', 1, None, True),
        )),
        ('storage', 'Storage configuration (S3 or Minio)', (
            ('url', 'Storage url', 'str', 'http://localhost:9000', None, True),
            ('bucket_name', 'Storage default private bucket', 'str', 'tesla', None, True),
            ('public_bucket_name', 'Storage default public bucket', 'str', 'tesla-public', None, True),
            ('region', 'Storage region', 'str', 'eu-west-1', None, True),
            ('access_key', 'Storage access key id', 'str', None, None, True),
            ('secret_key', 'Storage secret access key', 'str', None, None, True),
            ('ssl_verify', 'Verify SSL', 'bool', True, None, True),
        )),
        ('celery', 'Celery configuration (RabbitMQ or SQS)', (
            ('broker_protocol', 'Protocol to communicate with brocker', 'enum', 'amqp', ['amqp', 'sqs'], True),
            ('broker_user', 'User to authenticate with RabbitMQ or KEY for Amazon SQS', 'str', None, True),
            ('broker_password', 'Password to authenticate with RabbitMQ or SECRET for Amazon SQS', 'str', None, True),
            ('broker_host', 'Host for RabbitMQ', 'str', 'localhost', True),
            ('broker_region', 'Region for Amazon SQS', 'str', 'eu-west-1', True),
            ('broker_port', 'Port for RabbitMQ', 'int', 5672, True),
            ('broker_vhost', 'RabbitMQ Virtual Host', 'str', '/', True),
            ('queue_default', 'Name of the default queue used for periodic tasks', 'str', 'tesla', True),
            ('queue_enrolment', 'Name of the default queue for enrolment', 'str', 'tesla_enrolment', True),
            ('queue_enrolment_storage', 'Name of the storage queue for enrolment', 'str',
             'tesla_enrolment_storage', True),
            ('queue_enrolment_validation', 'Name of the validation queue for enrolment', 'str',
             'tesla_enrolment_validate', True),
            ('queue_verification', 'Name of the default queue for verification', 'str', 'tesla_verification', True),
            ('queue_alerts', 'Name of the default queue for alerts', 'str', 'tesla_alerts', True),
            ('queue_reporting', 'Name of the default queue for reports', 'str', 'tesla_reporting', True),
            ('queues', 'List of queues a worker will listen to.', 'list', None, False),
        )),
        ('rabbitmq', 'RabbitMQ configuration (only used for RabbitMQ deployment)', (
            ('erlang_cookie', 'Erlang Cookie value used for RabbitMQ cluster', 'str', None, True),
            ('admin_user', 'Administrator user to authenticate with RabbitMQ', 'str', None, True),
            ('admin_password', 'Administrator password to authenticate with RabbitMQ', 'str', None, True),
            ('admin_port', 'Port for the administration api of RabbitMQ', 'int', 15672, True),
            ('port', 'Port for the amqp api of RabbitMQ', 'int', 5672, True),
            ('host', 'Host name of the RabbitMQ server', 'str', 'localhost', True),
        )),
        ('django', 'DJango configuration', (
            ('secret_key', 'DJango secret value', 'str', None, None, True),
            ('allowed_hosts', 'Allowed hosts', 'list', [], None, True),
        )),
        ('deployment', 'Deployment configuration', (
            ('orchestrator', 'Docker orchestrator', 'enum', 'swarm', ['swarm', ], True),
            ('services', 'Deploy external services', 'bool', False, None, True),
            ('lb', 'Load balancer', 'enum', 'traefik', ['traefik', ], True),
            ('image', 'Docker image used for deployment', 'str',
             'teslace/core', None, True),
            ('version', 'Docker image version used for deployment', 'str', 'latest', None, True),
            ('secrets_path', 'Folder where secrets will be mounted', 'str', '/run/secrets', None, True),
            ('data_path', 'Folder where volumes will be persisted', 'str', '/var/tesla', None, True),
            ('specialized_workers', 'If enabled, specialized workers will be deployed.', 'bool', True, True),
        )),
        ('moodle', 'Moodle configuration. Only required if Moodle is deployed by TeSLA', (
            ('deploy', 'Deploy Moodle', 'bool', False, None, True),
            ('name', 'Unique VLE name in TeSLA', 'str', 'default_moodle', True),
            ('admin_user', 'Administrator user for Moodle', 'str', 'moodle', True),
            ('admin_password', 'Administrator password for Moodle', 'str', None, True),
            ('admin_email', 'Administrator email for Moodle', 'str', None, True),
            ('db_host', 'Host for Moodle database', 'str', None, None, True),
            ('db_port', 'Port for Moodle database', 'int', 3306, None, True),
            ('db_name', 'Database name for Moodle database', 'str', 'moodle', None, True),
            ('db_user', 'User for Moodle database', 'str', 'moodle', None, True),
            ('db_password', 'Password for Moodle database', 'str', None, None, True),
            ('db_prefix', 'Prefix for Moodle tables in the database', 'str', 'mdl_', None, True),
            ('cron_interval', 'Moodle Cron interval', 'int', 15, None, True),
            ('full_name', 'Full name for Moodle instance', 'str', 'TeSLA CE Moodle', None, True),
            ('short_name', 'Short name for Moodle instance', 'str', 'TeSLA CE', None, True),
            ('summary', 'Summary for Moodle instance', 'str', 'TeSLA CE Moodle Instance', None, True),
        ))
    )

    def __init__(self):
        """ Default class constructor """

        #: Configuration values contained in this class
        self._config = dict()

    def set(self, key, value=None):
        """
            Set a configuration value

            :param key: Configuration key
            :type key: str
            :param value: Configuration value
            :type value: object
            :exception TeslaConfigException: If the key is not valid or value type is incorrect
        """
        parts = self._get_field_parts(key)
        if parts is None:
            raise TeslaConfigException('Invalid configuration key {}'.format(key))
        field_desc = self._get_config_field(parts[0], parts[1])
        if field_desc is None:
            raise TeslaConfigException('Invalid configuration key {}'.format(key))
        self._config[key] = self._convert(value, field_desc)

    def get(self, key, default=None):
        """
            Get a configuration value

            :param key: Configuration key
            :type key: str
            :param default: Default value in case the key does not exist in the configuration
            :type default: object
            :return: Value assigned to the key or the default value provided
            :rtype: str | int | list | bool
            :exception TeslaConfigException: If the key is not valid
        """
        if key.upper() in self._config:
            return self._config[key.upper()]

        parts = self._get_field_parts(key)
        if parts is None:
            raise TeslaConfigException('Invalid configuration key {}'.format(key))
        field_desc = self._get_config_field(parts[0], parts[1])

        value = field_desc[3]
        if value is not None:
            return value

        return default

    def update(self, config):
        """
            Update configuration object with given options

            :param config: Configuration options
        """
        if isinstance(config, configparser.ConfigParser):
            # Update from config parser object
            for section in list(config):
                prefix = section.upper() + '_'
                if section == 'DEFAULT':
                    prefix = ''
                for s_key in config[section]:
                    key = s_key.upper()
                    if not key.startswith(prefix):
                        key = prefix + key
                    value = config.get(section, s_key, raw=True)
                    self.set(key, value)
        else:
            raise NotImplementedError

    def _get_config_field(self, section, key):
        """
            Get the description of a given configuration key

            :param section: Configuration section
            :param key: Configuration key
            :return: Tuple with field description or None if field does not exist
            :rtype: tuple
        """
        for sec in self._sections:
            if sec[0].upper() == section.upper():
                for s_key in sec[2]:
                    if s_key[0].upper() == key.upper():
                        return s_key
        return None

    @classmethod
    def get_sections(cls):
        """
            Get configuration sections

            :return: Configuration sections with values
            :rtype: dict
        """
        return cls._sections

    @staticmethod
    def _convert(value, desc):
        """
            Convert given value to the type of the field

            :param value: Provided value
            :type value: str | object
            :param desc: Field description tuple
            :type desc: tuple
            :return: Converted value
            :rtype: object
            :exception TeslaConfigException: If the value type is incorrect
        """
        if value is None:
            return None
        if isinstance(value, str) and len(value) == 0:
            return None
        field_type = desc[2]
        type_opt = desc[4]
        if field_type == 'str':
            return str(value)
        if field_type == 'bool':
            if isinstance(value, bool):
                return value
            if isinstance(value, int):
                return value == 1
            if isinstance(value, str):
                return value.upper() in ['TRUE', 'YES', 'Y', '1']
            raise TeslaConfigException('Invalid value for configuration key {}. Expected {}'.format(
                desc[0], field_type))
        if field_type == 'int':
            try:
                return int(value)
            except:
                raise TeslaConfigException('Invalid value for configuration key {}. Expected {}'.format(
                    desc[0], field_type))
        if field_type == 'enum':
            if value not in type_opt:
                raise TeslaConfigException('Invalid value for configuration key {}. Valid values are {}'.format(
                    desc[0], type_opt))
            return value
        if field_type == 'list':
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                return value.split(',')
            raise TeslaConfigException('Invalid value for configuration key {}. Expected {}'.format(
                desc[0], field_type))
        # Valid types are processed on previous lines
        raise TeslaConfigException('Invalid type {} in field description'.format(field_type))

    def _get_field_parts(self, key):
        """
            Get the section and field values form a given configuration key
            :param key: Configuration key
            :type key: str
            :return: Tuple with section and field name or None if it is not a valid key
            :rtype: tuple
        """
        key = key.upper()
        for sec in self._sections:
            prefix = sec[0].upper() + '_'
            if key.startswith(prefix):
                section = sec[0].upper()
                field = key.split(prefix)[1]
                for s_field in sec[2]:
                    if field == s_field[0].upper():
                        return section, field
                return None
        return None

    def is_valid_key(self, key):
        """
            Check if a configuration key is valid or not

            :param key: The configuration key to be checked
            :type key: str
            :return: True if the key is valid or False otherwise
            :rtype: bool
        """
        return self._get_field_parts(key) is not None

    def get_config(self):
        """
            Get all configuration values

            :return: Dictionary with configuration
            :rtype: dict
        """
        conf = {}

        for section in self._sections:
            conf[section[0]] = {}
            for key in section[2]:
                conf[section[0]][key[0]] = {
                    'value': self.get('{}_{}'.format(section[0], key[0]).upper()),
                    'description': key[1]
                }
        return conf

    def get_config_kv(self):
        """
            Get all configuration values as a key-value dictionary

            :return: Dictionary with configuration kv
            :rtype: dict
        """
        conf = {}

        for section in self._sections:
            for key in section[2]:
                full_key = '{}_{}'.format(section[0], key[0]).upper()
                conf[full_key] = self.get(full_key)
        return conf

    def write(self, file_handler):
        """
            Write configuration to a file

            :param file_handle: File handler where configuration will be written
            :type file_handle: file
        """
        for section in self.get_sections():
            # Write the section header
            self._write_section_header(section, file_handler)
            for key in section[2]:
                # Skip keys with export flag to False
                if len(key) > 5 and not key[5]:
                    continue
                # Write key
                self._write_key(section, key, file_handler)
            file_handler.write('\n')

    @staticmethod
    def _write_section_header(section, file_handler):
        """
            Write configuration section header to a file

            :param section: Section description tuple
            :type section: tuple
            :param file_handle: File handler where it will be written
            :type file_handle: file
        """
        file_handler.write('# {}\n'.format(section[1]))
        file_handler.write('[{}]\n'.format(section[0]))

    @staticmethod
    def _write_key_header(key, file_handler):
        """
            Write configuration key header to a file

            :param key: Key description tuple
            :type key: tuple
            :param file_handle: File handler where it will be written
            :type file_handle: file
        """
        type = key[2]
        value = key[3]
        if type == 'enum':
            type = ' | '.join(key[4])
        elif type == 'list' and value is not None:
            value = ','.join(value)
        file_handler.write('# {}\n'.format(key[1]))
        file_handler.write('# ({})'.format(type))
        if value is not None and len(str(value)) > 0:
            file_handler.write(' default: {}'.format(value))
        file_handler.write('\n')

    def _write_key(self, section, key, file_handler):
        """
            Write configuration key information to a file

            :param section: Section description tuple
            :type section: tuple
            :param key: Key description tuple
            :type key: tuple
            :param file_handle: File handler where it will be written
            :type file_handle: file
        """
        # Write the key header
        self._write_key_header(key, file_handler)

        # Get current value
        value = self.get('{}_{}'.format(section[0], key[0]).upper())
        if key[2] == 'list' and value is not None:
            value = ','.join(value)
        if value is not None:
            value = str(value)

        # Get the default value as string
        default_value = key[3]
        if key[2] == 'list' and default_value is not None:
            default_value = ','.join(default_value)
        if default_value is not None:
            default_value = str(default_value)

        # Store the key
        if default_value is None and value is None:
            file_handler.write('{}=\n'.format(key[0]))
        elif value is not None and value != default_value:
            file_handler.write('{}={}\n'.format(key[0], value))
        else:
            file_handler.write('# {}={}\n'.format(key[0], default_value))
