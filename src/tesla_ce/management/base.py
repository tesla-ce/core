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
""" Base Command for TeSLA CE """
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from tesla_ce.client import Client
from tesla_ce.client import ConfigManager


class TeslaCommand(BaseCommand):
    """ Base Command class for TeSLA CE """

    # TeSLA CE client instance
    _client: Client = None

    # Configuration file
    _conf_file = None

    # Execution options
    _options = None

    # Enable if configuration file is required
    _conf_file_required = False

    @staticmethod
    def get_client(config_file=None, options=None):
        """
            Create an instance of the client
            :param config_file: Path to the configuration file
            :param options: Provided options to the command
            :return: Instance of client
        """
        return Client(config=settings.TESLA_CONFIG, use_vault=False, use_env=False, enable_management=True)

    @staticmethod
    def get_config_file(options=None):
        """
            Get the configuration file
            :param options: Provided options to the command
            :return: Instance of client
        """
        # Get value in environment
        config_file = settings.TESLA_CONFIG.config.get('TESLA_CONFIG_FILE')
        if config_file is None:
            # Check default paths
            config_file = ConfigManager.find_config_file()

        return config_file

    @property
    def client(self):
        """
            Access to the TeSLA CE client
            :return: Instance of the client
        """
        if self._client is None:
            self._client = self.get_client(self.conf_file, self._options)
        return self._client

    @property
    def conf_file(self):
        """
            Access to the configuration file
            :return: Path to the configuration file
        """
        if self._conf_file is None:
            self._conf_file = self.get_config_file(self._options)
        return self._conf_file

    def print_version(self):
        """
            Print current software version
        """
        self.stdout.write('TeSLA CE version {}'.format(self.client.version))

    def check_configuration_file(self):
        """
            Check if the defined configuration file exists
        """
        # Check if file exists or not
        if self._conf_file is None:
            if self._conf_file_required:
                raise CommandError('Configuration file not found')
            else:
                self.stdout.write('Configuration file not found: {}'.format(self.style.WARNING('[WARINING]')))
        else:
            if os.path.exists(self.conf_file):
                self.stdout.write('Reading configuration from {}: {}'.format(self.conf_file,
                                                                             self.style.SUCCESS('[OK]')))
            else:
                if self._conf_file_required:
                    self.stdout.write('Reading configuration from {}: {}'.format(self.conf_file,
                                                                                 self.style.ERROR('[ERROR]')))
                    raise CommandError('Configuration file not found')
                else:
                    self.stdout.write('Error reading configuration from {}: {}'.format(self.conf_file,
                                                                                       self.style.WARINING('[WARNING]'))
                                      )

    def handle(self, *args, **options):
        """
            Perform command actions
            :param args: List of arguments
            :param options: List of named options
        """
        # Store options
        self._options = options

        # Print current version
        self.print_version()

        # Check configuration file
        self.check_configuration_file()

        # Perform custom actions
        self.custom_handle()

    def custom_handle(self):
        """
            Custom actions for each command
        """
        # This method is implemented in the commands
        pass


class TeslaConfigCommand(TeslaCommand):
    """ Base Configuration Command class for TeSLA CE """

    _conf_file_required = True

    @staticmethod
    def get_config_file(options=None):
        """
            Get the configuration file
            :param options: Provided options to the command
            :return: Instance of client
        """
        # Search for configuration file
        if options is not None and options['local']:
            config_file = 'tesla-ce.cfg'
        else:
            config_file = ConfigManager.find_config_file()

        return config_file

    @staticmethod
    def get_client(config_file=None, options=None):
        """
            Create an instance of the client
            :param config_file: Path to the configuration file
            :param options: Provided options to the command
            :return: Instance of client
        """
        return Client(config_file=config_file, use_vault=False, use_env=False, enable_management=True)

    def _get_configuration_report(self, allow_invalid=False):
        """
            Check if current configuration is valid
            :return: Configuration report
        """
        # Check the configuration
        self.stdout.write('Checking current configuration')
        report = self.client.check_configuration()
        if report['valid']:
            self.stdout.write(
                self.style.SUCCESS('Configuration file is {}.'.format(self.style.SUCCESS('valid')))
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Configuration file is {}.'.format(self.style.ERROR('not valid')))
            )
            if not allow_invalid:
                self.stdout.write(self.style.ERROR('Invalid configuration. Use --check option for details'))
                raise CommandError('Invalid configuration')

            for service in report:
                if isinstance(report[service], dict) and not report[service]['valid']:
                    self.stdout.write('Checking service {}: {}'.format(service, self.style.ERROR('[ERROR]')))
                    for err in report[service]['errors']:
                        self.stdout.write(self.style.ERROR('\t- {}'.format(err)))
            self.stdout.write(
                self.style.ERROR('Configuration errors. Check provided errors.'))

        return report


class TeslaDeployCommand(TeslaCommand):
    """ Base Deployment Command class for TeSLA CE """

    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        parser.add_argument(
            '--mode',
            choices=['swarm'],
            help='Type of deployment',
        )
        parser.add_argument(
            '--out',
            default='./deploy',
            help='Directory where configuration files will be written.',
        )
