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
""" DJango command to register a new Provider to TeSLA system """
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from tesla_ce.client import Client


class Command(BaseCommand):
    help = 'Register a new Provider to TeSLA CE system'
    requires_system_checks = '__all__'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='If the Provider already exist, update the information and generate new credentials',
        )
        parser.add_argument(
            'provider_file',
            help='Provider description file',
        )

    def handle(self, *args, **options):

        # Check the configuration
        config_file = settings.TESLA_CONFIG.config.get('TESLA_CONFIG_FILE')
        if os.path.exists(config_file):
            self.stdout.write('Reading configuration from {}: {}'.format(config_file,
                                                                         self.style.SUCCESS('[OK]')))
        else:
            self.stdout.write('Reading configuration from {}: {}'.format(config_file,
                                                                         self.style.ERROR('[ERROR]')))
            raise CommandError('Configuration file not found')

        provider_file = options['provider_file']
        if os.path.exists(provider_file):
            try:
                with open(provider_file, 'r') as fd_provider:
                    provider_desc = json.load(fd_provider)
                    self.stdout.write('Reading provider description from {}: {}'.format(provider_file,
                                                                                        self.style.SUCCESS('[OK]')))
            except Exception as exc:
                self.stdout.write('Reading provider description from {}: {}: {}'.format(provider_file,
                                                                                        self.style.ERROR('[ERROR]'),
                                                                                        exc))
        else:
            self.stdout.write('Reading configuration from {}: {}'.format(config_file,
                                                                         self.style.ERROR('[ERROR]')))
            raise CommandError('Configuration file not found')

        # Create a client
        client = Client(config=settings.TESLA_CONFIG, use_vault=False, use_env=False, enable_management=True)

        # Get arguments
        force_update = options['force_update']

        # Register the new VLE
        provider_info = client.register_provider(provider_desc, force_update)

        self.stdout.write('Provider registered. Use this configuration: {}'.format(
            json.dumps(provider_info, indent=4, sort_keys=True),
            self.style.SUCCESS('[OK]'))
        )
