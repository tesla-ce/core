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
""" DJango command to generate the configuration file for TeSLA system """
from ..base import TeslaDeployCommand


class Command(TeslaDeployCommand):
    """ Command to generate deployment files for services """
    help = 'Generates configuration files to deploy the TeSLA CE required services'
    requires_system_checks = []

    def custom_handle(self):
        """
            Custom actions for this command
        """
        # Export the deployment scripts
        self.client.export_services_scripts(output=self._options['out'], mode=self._options['mode'])
        self.stdout.write(self.style.SUCCESS('Deployment scripts written at {}'.format(self._options['out'])))
