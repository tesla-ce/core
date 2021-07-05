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
""" DJango command to register a new VLE to TeSLA system """
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from tesla_ce.client import Client


class Command(BaseCommand):
    help = 'Register a new VLE to TeSLA CE system'
    requires_system_checks = '__all__'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['moodle'],
            default='moodle',
            help='Type of VLE',
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='If the VLE already exist, update the information and generate new credentials',
        )
        parser.add_argument(
            '--url',
            help='URL of the VLE',
            default=None,
        )
        parser.add_argument(
            '--client-id',
            help='Client ID for LTI 1.3',
            default=None,
        )
        parser.add_argument(
            'name',
            help='Unique name for the VLE',
        )
        parser.add_argument(
            '--institution',
            help='The acronym of the institution this VLE belongs to',
            default=None,
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

        # Create a client
        client = Client(config=settings.TESLA_CONFIG, use_vault=False, use_env=False, enable_management=True)

        # Get arguments
        type = options['type']
        name = options['name']
        url = options['url']
        client_id = options['client_id']
        institution_acronym = options['institution']
        force_update = options['force_update']

        # Register the new VLE
        vle_info = client.register_vle(type, name, url, institution_acronym, client_id, force_update)

        self.stdout.write('VLE registered. Use this configuration: {}'.format(
            json.dumps(vle_info, indent=4, sort_keys=True),
            self.style.SUCCESS('[OK]'))
        )
