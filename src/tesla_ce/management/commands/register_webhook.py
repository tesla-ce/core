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
from django.core.management.base import CommandError

from ..base import TeslaDeployCommand


class Command(TeslaDeployCommand):
    """ Command to register Providers and optionally generate their deployment scripts """
    help = 'Register a new Webhook to TeSLA CE system'
    requires_system_checks = '__all__'

    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        # Set default arguments
        super().add_arguments(parser)

        parser.add_argument(
            '--credentials',
            help='Register webhook with this credentials',
        )
        parser.add_argument(
            '--name',
            help='Name of the webhook',
        )
        parser.add_argument(
            '--client_header',
            help='Client header of the webhook',
        )
        parser.add_argument(
            '--id_header',
            help='Id header of the webhook',
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """

        name = self._options['name']
        client_header = self._options['client_header']
        id_header = self._options['id_header']
        credentials = self._options['credentials']

        provider_info = self.client.register_webhook(name, client_header, id_header, credentials)
        self.stdout.write(self.style.SUCCESS('Webhook registered correctly'))
