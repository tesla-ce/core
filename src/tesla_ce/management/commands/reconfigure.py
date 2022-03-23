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
""" DJango command to perform the configuration of TeSLA system """
from django.core.management.base import CommandError

from tesla_ce.client import Client
from ..base import TeslaConfigCommand


class Command(TeslaConfigCommand):
    """ Reconfiguration command """
    help = 'Reconfigure TeSLA CE system'
    requires_system_checks = []

    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        parser.add_argument(
            '--local',
            action='store_true',
            help='Use the configuration file in current directory',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check the configuration, but do not perform the installation',
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """

        # Get configuration report
        report = self._get_configuration_report(self._options['check'])

        if report['valid']:
            # Performing reconfiguration
            self.stdout.write('Configuring TeSLA CE')

            # Initialize TeSLA
            self.client.initialize()
