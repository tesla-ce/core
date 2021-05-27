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
""" Utility module to perform system checks"""
import hvac
from django.db.utils import ConnectionHandler
from django.db.utils import OperationalError
from requests.exceptions import ConnectionError


def check_vault_connection(config):
    """
        Check HashiCorp Vault status

        :param config: Configuration object
        :return: Report of the status
        :rtype: dict
    """
    # Create a new Vault client
    client = hvac.Client(url=config.get('VAULT_URL'), verify=config.get('VAULT_SSL_VERIFY'))

    # Initialize the report
    report = {}

    # Try to connect vault
    try:
        is_initialized = client.sys.is_initialized()
        report['connected'] = True
        report['initialized'] = is_initialized
    except ConnectionError as e:
        report['connected'] = False
        report['error'] = e

    if report['connected'] and report['initialized']:
        report['sealed'] = client.sys.is_sealed()

    report['ready'] = report['connected'] and report['initialized'] and not report['sealed']

    return report


def check_database_connection(config):
    """
        Check Database status

        :param config: Configuration object
        :return: Report of the status
        :rtype: dict
    """
    # Define the databases
    databases = {
        'admin': {
            'ENGINE': 'django.db.backends.{}'.format(config.get('DB_ENGINE')),
            'HOST': config.get('DB_HOST'),
            'PORT': config.get('DB_PORT'),
            'USER': config.get('DB_ROOT_USER'),
            'PASSWORD': config.get('DB_ROOT_PASSWORD'),
            'NAME': ''
        },
        'default': {
            'ENGINE': 'django.db.backends.{}'.format(config.get('DB_ENGINE')),
            'HOST': config.get('DB_HOST'),
            'PORT': config.get('DB_PORT'),
            'USER': config.get('DB_USER'),
            'PASSWORD': config.get('DB_PASSWORD'),
            'NAME': config.get('DB_NAME'),
        },
    }

    # Create the connections
    connection = ConnectionHandler()
    connection.configure_settings(databases=databases)

    # Check connections
    report = {}
    for db in databases:
        report[db] = {}
        try:
            connection[db].cursor()
            report[db]['connected'] = True
        except OperationalError as e:
            report[db]['connected'] = False
            report[db]['error'] = e
        except Exception as e:
            report[db]['connected'] = False
            report[db]['error'] = e

    return report


def check_vault_configuration(config):
    """
        Check HashiCorp Vault configuration

        :param config: Configuration object
        :return: Report of the configuration check
        :rtype: dict
    """
    valid = True
    errors = []

    # Check URL
    if config.get('VAULT_URL') is None:
        valid = False
        errors.append('Vault URL is not provided')
    elif not config.get('VAULT_URL').startswith('https://') and not config.get('VAULT_URL').startswith('http://'):
        valid = False
        errors.append('Vault URL schema is not provided. Use http or https.')

    # Check connection
    if valid:
        config_report = check_vault_connection(config)
        if not config_report['connected']:
            valid = False
            errors.append('Cannot connect with Vault: {}'.format(config_report['error']))
        else:
            if config_report['initialized']:
                if config.get('VAULT_TOKEN') is None:
                    valid = False
                    errors.append('Vault is initialized, but root token is not provided')
                if config_report['sealed'] and \
                        (config.get('VAULT_KEYS') is None or len(config.get('VAULT_KEYS')) == 0):
                    valid = False
                    errors.append('Vault is sealed, but unseal keys are not provided')
    else:
        config_report = {
            'connected': False
        }

    # Add final status and errors
    config_report['valid'] = valid
    config_report['errors'] = errors

    return config_report


def check_db_configuration(config):
    """
        Check Database configuration

        :param config: Configuration object
        :return: Report of the configuration check
        :rtype: dict
    """
    valid = True
    connected = True
    errors = []
    config_report = {}

    # Check basic configuration
    if config.get('DB_ENGINE') is None:
        valid = False
        errors.append('Database engine not provided')
    if config.get('DB_HOST') is None:
        valid = False
        errors.append('Database host not provided')
    if config.get('DB_PORT') is None:
        valid = False
        errors.append('Database port not provided')
    if (config.get('DB_USER') is None or config.get('DB_PASSWORD') is None) and \
        (config.get('DB_ROOT_USER') is None or config.get('DB_ROOT_PASSWORD') is None):
        valid = False
        errors.append('Database credentials not provided.')
    if valid:
        config_report['databases'] = check_database_connection(config)
        if not config_report['databases']['default']['connected'] and \
                not config_report['databases']['admin']['connected']:
            connected = False
            errors.append('Cannot connect to database.')

    config_report['valid'] = valid
    config_report['connected'] = connected
    config_report['errors'] = errors
    return config_report


def check_tesla_configuration(config):
    """
        Check general TeSLA configuration

        :param config: Configuration object
        :return: Report of the configuration check
        :rtype: dict
    """
    valid = True
    errors = []

    if config.get('TESLA_DOMAIN') is None:
        valid = False
        errors.append('TeSLA domain is missing')

    if config.get('TESLA_ADMIN_MAIL') is None:
        valid = False
        errors.append('TeSLA administrator email is missing')

    return {
        'valid': valid,
        'errors': errors
    }
