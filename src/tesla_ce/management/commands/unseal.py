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
""" DJango command to perform the initial setup of TeSLA system """
import os

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from tesla_ce.client import Client
from tesla_ce.client import ConfigManager
from ..base import TeslaConfigCommand


class Command(TeslaConfigCommand):
    """ Command to unseal Vault """
    help = 'Unseal Vault for TeSLA CE system'
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

    def custom_handle(self):
        """
            Custom actions for this command
        """

        # Get configuration report
        self._get_configuration_report()

        # Check if Vault is initialized
        if not self.client.vault.is_initialized():
            self.stdout.write(self.style.ERROR('Vault is not initialized. Please use initial_setup command.'))
            raise CommandError('Vault is not Initialized')

        # Check if Vault is sealed
        if not self.client.vault.is_sealed():
            self.stdout.write('Vault is not sealed. No action performed.')
        else:
            # Unseal Vault
            self.stdout.write('Unsealing Vault')
            self.client.vault.unseal()

        # Check final status
        if self.client.vault.is_sealed():
            self.stdout.write('Check Vault status: {}'.format(self.style.ERROR('[SEALED]')))
        else:
            self.stdout.write('Check Vault status: {}'.format(self.style.SUCCESS('[UNSEALED]')))
