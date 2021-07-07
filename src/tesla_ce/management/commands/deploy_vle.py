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
""" DJango command to generate deployment scripts for a VLE """
from ..base import TeslaDeployCommand


class Command(TeslaDeployCommand):
    """ Command to generate VLE deployment scripts """
    help = 'Generate VLE deployment scripts'
    requires_system_checks = '__all__'

    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        # Set default arguments
        super().add_arguments(parser)

        parser.add_argument(
            '--client-id',
            help='Client ID for LTI 1.3',
            default=None,
        )
        parser.add_argument(
            '--type',
            choices=['moodle'],
            default='moodle',
            help='Type of VLE',
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """
        # Export the deployment scripts
        self.client.export_vle_scripts(
            type=self._options['type'],
            client_id=self._options['client_id'],
            output=self._options['out'],
            mode=self._options['mode'])
        self.stdout.write(self.style.SUCCESS('Deployment scripts written at {}'.format(self._options['out'])))
