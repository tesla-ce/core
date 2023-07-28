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
import django.db.utils
import requests
import os
import json
from io import StringIO
from django.core.management import call_command
from django.core.management.base import CommandError

from tesla_ce.client import ConfigManager
from tesla_ce.lib.exception import TeslaConfigException
from tesla_ce.lib.exception import TeslaDatabaseException
from ..base import TeslaConfigCommand


class Command(TeslaConfigCommand):
    """ Reconfiguration command """
    help = 'Remote setup TeSLA CE system'
    requires_system_checks = []
    report_errors = {}

    @staticmethod
    def get_config_file(options=None):

        url = os.getenv('SUPERVISOR_REMOTE_URL')
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            config = response.json()
            conf_manager = ConfigManager(load_config=False)
            output_file = './tesla-ce.cfg'

            # Check that output folder exists
            if not os.path.exists(os.path.dirname(output_file)):
                os.makedirs(os.path.dirname(output_file))

            for section in config:
                for item_key in config[section]:
                    config_key = "{}_{}".format(section, item_key).upper()
                    if config[section][item_key]['value'] is not None:
                        conf_manager.config.set(config_key, config[section][item_key]['value'])

            # Write the configuration file to disk
            conf_manager.save_configuration()
        else:
            content = response.content
            if content is not None:
                content = content.decode('utf8')
            else:
                content = ''

            raise CommandError("Cannot get remote configuration. Server returns status code {}. Response content {}.".format(response.status_code, content))

        return 'tesla-ce.cfg'

    # todo: implement
    def report_remote_result(self, status):
        command = self._options.get('command')

        url = os.getenv('SUPERVISOR_REMOTE_URL')
        data = {
            "status": status,
            "command": command
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('All data was sended to supervisor'))
            else:
                self.stdout.write(self.style.ERROR('Data was not sended to supervisor. Response status code: {}. '
                                                   'Response content: {}'.format(response.status_code,
                                                                                 response.content)))
        except Exception as err:
            self.stdout.write(self.style.ERROR('Data was not sended to supervisor: {}'.format(str(err))))

    # todo: tesla_ce remote_setup --command=vault_init_kv --url=https://xxxx
    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        parser.add_argument(
            '--command',
            help='Check the configuration, but do not perform the installation',
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """

        # Get configuration report
        command = self._options.get('command')

        valid_commands = [
            'vault_unseal'
            'vault_init_kv',
            'vault_init_policies',
            'vault_init_transit',
            'vault_init_roles',
            'migrate_database',
            'collect_static',
            'load_fixtures',
            'create_superuser',
            'register_tpt_webhook'
        ]

        status = {"status": False, "info": {}}

        if command not in valid_commands:
            status['info'] = "Command [{}] is not valid".format(command)

        if command in ['vault_unseal', 'vault_init_kv', 'vault_init_transit', 'vault_init_policies',
                       'vault_init_roles']:
            status = self.client.vault.remote_setup(command)
            status['status'] = status['command_status']

        elif command in ['migrate_database']:
            from django.conf import settings

            try:
                self.client.database.apply_migrations()
                # Update messages
                self.client.database.update_default_messages()

                # Set default institution
                self.client.database.update_default_institution()

                # Set default instruments
                self.client.database.update_default_instruments()

                # Create periodic tasks
                self.client.database.update_periodic_tasks()

                status['status'] = True
            except django.db.utils.Error as err:
                status['info'] = str(err)

        elif command in ['collect_static']:
            try:
                out = StringIO()
                err_out = StringIO()
                call_command('collectstatic', verbosity=3, interactive=False, stdout=out, stderr=err_out)

                out.seek(0)
                err_out.seek(0)

                status['info']['stout'] = out.read()
                status['info']['sterr'] = err_out.read()
                status['status'] = True
            except Exception as err:
                status['info'] = str(err)

        elif command in ['load_fixtures']:
            try:
                out = StringIO()
                err_out = StringIO()
                call_command('loaddata', 'ui_options', verbosity=3, stdout=out, stderr=err_out)

                out.seek(0)
                err_out.seek(0)

                status['info']['stout'] = out.read()
                status['info']['sterr'] = err_out.read()
                status['status'] = True
            except Exception as err:
                status['info'] = str(err)
        elif command in ['create_superuser']:
            try:
                self.client.database.create_superuser(username=self.client.config.config.get('tesla_admin_mail'),
                                                      password=self.client.config.config.get('tesla_admin_password'),
                                                      email=self.client.config.config.get('tesla_admin_mail')
                                                      )
                status['status'] = True
            except TeslaDatabaseException as exc:
                status['status'] = False
                status['info'] = str(exc)
        elif command in ['register_tpt_webhook']:
            try:
                name = 'tpt'
                client_header = 'TESLA-TPT-METHOD'
                id_header = 'TESLA-TPT-MESSAGE-ID'
                credentials = "{\"secret\": \""+self.client.config.config.get('tpt_service_api_secret')+"\"}"
                provider_info = self.client.register_webhook(name, client_header, id_header, credentials)
                status['status'] = True
            except Exception as err:
                status['status'] = False
                status['info'] = str(err)

        self.report_remote_result(status=status)
