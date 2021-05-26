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
""" Database Manager Module"""
import json
import os
import uuid

from django.db import connections
from django.db.migrations.executor import MigrationExecutor

from tesla_ce.lib import ConfigManager
from tesla_ce.lib.checks import check_database_connection
from tesla_ce.lib.exception import TeslaDatabaseException


class DatabaseManager:
    """ Manager class for Databases """

    def __init__(self, config=None):
        """
            Default constructor
            :param config: Configuration manager instance
            :type config: ConfigManager
        """
        if config is None:
            config = ConfigManager()

        # Store the configuration object
        self._config = config

    def initialize(self):
        """
            Initialize the database
        """
        # Get the connection status
        connection_status = self.check_connection()

        # Check database
        if not connection_status['default']['connected'] and not connection_status['admin']['connected']:
            raise TeslaDatabaseException('Cannot connect to the database {}@{}:{}/{}'.format(
                self._config.config.get('DB_USER'),
                self._config.config.get('DB_HOST'),
                self._config.config.get('DB_PORT'),
                self._config.config.get('DB_NAME')
            ))

        # Create TeSLA database if it does not exist
        if not connection_status['default']['connected']:
            # Create a password if it does not exist
            if self._config.config.get('DB_PASSWORD') is None:
                new_password = uuid.uuid4().__str__()
                self._config.config.set('DB_PASSWORD', new_password)
                self._config.save_configuration()
            # Create the database
            self.create_database()
            # Create the user
            self.create_user()

            # Check connection
            connection_status = self.check_connection()
            if not connection_status['default']['connected']:
                raise TeslaDatabaseException('Database and user creation failed')

            # Save created credentials
            self._config.save_configuration()

        # Apply migrations
        self.apply_migrations()

        # Update messages
        self.update_default_messages()

        # Set default institution
        self.update_default_institution()

        # Set default instruments
        self.update_default_instruments()

        # Create periodic tasks
        self.update_periodic_tasks()

    def check_connection(self):
        """
            Check database connection and access
        """
        return check_database_connection(config=self._config.config)

    def version(self):
        """
            Get the version of the database structure

            :return: Version of the database or None if no migration is applied
            :rtype: int
        """
        status = self._check_migrations()
        return status['current_version']

    def apply_migrations(self):
        """
            Apply pending migrations to the database

            :return: Result of the migration
        """
        status = self._check_migrations(admin=True)
        migration = status['executor'].migrate(targets=status['targets'],
                                               plan=status['plan'])
        return migration

    def create_database(self, name=None):
        """
            Create new database
        """
        engine = self._config.config.get('DB_ENGINE')
        creation_db_params = connections['admin'].get_connection_params()
        creation_db_params['db'] = ''
        creation_db = connections['admin'].get_new_connection(creation_db_params)
        cursor = creation_db.cursor()
        if name is None:
            name = self._config.config.get('DB_NAME')
        if engine == 'mysql':
            cursor.execute('CREATE DATABASE IF NOT EXISTS {};'.format(name))
        elif engine == 'postgresql':
            cursor.execute(
                'SELECT \'CREATE DATABASE {}\' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = \'{}\')\\gexec'.format(
                    name, name)
            )
        else:
            raise TeslaDatabaseException('Unsuported engine {}'.format(engine))

    def create_user(self, db_name=None, db_user=None, db_password=None):
        """
            Create a new user for a database
        """
        # TODO: Implement different versions depending on Engine
        engine = self._config.config.get('DB_ENGINE')
        cursor = connections['admin'].cursor()

        if db_name is None:
            db_name = self._config.config.get('DB_NAME')
        if db_user is None:
            db_user = self._config.config.get('DB_USER')
        if db_password is None:
            db_password = self._config.config.get('DB_PASSWORD')

        if engine == 'mysql':
            cursor.execute('GRANT ALL PRIVILEGES ON {}.* TO \'{}\'@\'%\' IDENTIFIED BY \'{}\';'.format(
                db_name,
                db_user,
                db_password
            ))
        elif engine == 'postgresql':
            raise NotImplementedError('PostgreSQL user creation not implemented')
        else:
            raise TeslaDatabaseException('Unsuported engine {}'.format(engine))

    def get_status(self):
        """
            Get the database status

            :return: Object with status information
            :rtype: dict
        """
        return {
            'status': 0,
            'warnings': 0,
            'errors': 0,
            'info': {}
        }

    def _get_executor(self, admin=False):
        """
            Create a migration executor
            :return: Executor object ready to access default database
        """
        connection = connections['default']
        if admin:
            connection = connections['admin']
        executor = MigrationExecutor(connection)
        executor.loader.check_consistent_history(connection)
        return executor

    def _check_migrations(self, admin=False):
        """
            Check migrations status
            :return: Migration status report
            :rtype: dict
        """
        # Get the executor
        executor = self._get_executor(admin)

        # Check for conflicts
        conflicts = executor.loader.detect_conflicts()

        # Get target migrations for all applications
        targets = executor.loader.graph.leaf_nodes()

        # Compute a migration plan
        plan = executor.migration_plan(targets)

        # Get TeSLA CE migrations newest version
        new_version = None
        for target_desc in targets:
            if target_desc[0] == 'tesla_ce':
                new_version = int(target_desc[1].split('_')[0])

        # Get TeSLA CE migrations current version
        current_version = None
        for plan_desc in plan:
            if plan_desc[0].app_label == 'tesla_ce':
                version = int(plan_desc[0].name.split('_')[0])
                if current_version is None or version < current_version:
                    current_version = version
        if current_version is None:
            # There are no migrations to apply. We are on the target migration
            current_version = new_version
        else:
            # If the lower migration to apply is the first one, there is no migration applied
            if current_version == 1:
                current_version = None
            else:
                current_version = current_version - 1

        return {
            'executor': executor,
            'targets': targets,
            'plan': plan,
            'conflicts': conflicts,
            'current_version': current_version,
            'new_version': new_version
        }

    def update_default_institution(self):
        """
            Update the information for the default institution
        """
        from tesla_ce.models import Institution
        try:
            default_institution = Institution.objects.get(pk=1)
            default_institution.name = self._config.config.get('TESLA_INSTITUTION_NAME')
            default_institution.acronym = self._config.config.get('TESLA_INSTITUTION_ACRONYM')
            default_institution.save()
        except Institution.DoesNotExist:
            Institution.objects.create(name=self._config.config.get('TESLA_INSTITUTION_NAME'),
                                       acronym=self._config.config.get('TESLA_INSTITUTION_ACRONYM'))

    def update_default_instruments(self):
        """
            Update the information for the default instruments
        """
        from tesla_ce.models import Instrument
        fr_vr_schema = json.dumps(
                    {
                        'type': 'object',
                        'properties': {
                            'online': {
                                'type': 'boolean',
                                'title': 'Analyze learner identity during the assessment',
                                'default': True
                            },
                            'offline': {
                                'type': 'boolean',
                                'title': 'Analyze learner identity on the delivered assessment',
                                'default': False
                            }
                        }
                    }
                )
        default_instruments = (
            {
                'id': 1, 'name': 'Face Recognition', 'acronym': 'fr', 'queue': 'tesla_fr',
                'requires_enrolment': True, 'identity': True, 'originality': False, 'authorship': False,
                'description': 'Verify learner identity by means of face attributes.',
                'options_schema': fr_vr_schema
            },
            {
                'id': 2, 'name': 'Keystroke Dynamics Recognition', 'acronym': 'ks', 'queue': 'tesla_ks',
                'requires_enrolment': True, 'identity': True, 'originality': False, 'authorship': False,
                'description': 'Verify learner identity by means of keystroke patterns.',
                'options_schema': None
            },
            {
                'id': 3, 'name': 'Voice Recognition', 'acronym': 'vr', 'queue': 'tesla_vr',
                'requires_enrolment': True, 'identity': True, 'originality': False, 'authorship': False,
                'description': 'Verify learner identity by means of voice attributes.',
                'options_schema': fr_vr_schema
            },
            {
                'id': 4, 'name': 'Forensic Analysis', 'acronym': 'fa', 'queue': 'tesla_fa',
                'requires_enrolment': True, 'identity': True, 'originality': False, 'authorship': True,
                'description': 'Verify learner identity by means of writing style patterns.',
                'options_schema': None
            },
            {
                'id': 5, 'name': 'Plagiarism Detection', 'acronym': 'plag', 'queue': 'tesla_plag',
                'requires_enrolment': False, 'identity': False, 'originality': True, 'authorship': False,
                'description': 'Verify the originality of an assessment.',
                'options_schema': None
            }
        )
        for inst in default_instruments:
            try:
                inst_obj = Instrument.objects.get(pk=inst['id'])
                inst_obj.name = inst['name']
                inst_obj.description = inst['description']
                inst_obj.acronym = inst['acronym']
                inst_obj.queue = inst['queue']
                inst_obj.requires_enrolment = inst['requires_enrolment']
                inst_obj.identity = inst['identity']
                inst_obj.originality = inst['originality']
                inst_obj.authorship = inst['authorship']
                inst_obj.options_schema = inst['options_schema']
                inst_obj.save()
            except Instrument.DoesNotExist:
                Instrument.objects.create(**inst)

    def update_default_messages(self):
        """
            Update the default messages
        """
        from tesla_ce.models import Message, MessageLocale

        messages_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'messages.csv'))

        with open(messages_file, 'r', encoding='latin-1') as msg_file:
            headers = msg_file.readline().replace('\n', '')
            header_parts = headers.split(';')
            languages = header_parts[4:]
            line = msg_file.readline().replace('\n', '')
            while line is not None and len(line) > 0:
                line_parts = line.split(';')
                msg, created = Message.objects.update_or_create(code=line_parts[0],
                                                                defaults={
                                                                    'datatype': line_parts[1],
                                                                    'description': line_parts[2],
                                                                    'meaning': line_parts[3]
                                                                })
                translations = line_parts[4:]
                for lang_code, translation in zip(languages, translations):
                    if len(translation) > 0:
                        MessageLocale.objects.update_or_create(code=msg,
                                                               locale=lang_code,
                                                               defaults={'message': translation})
                line = msg_file.readline()

    def update_periodic_tasks(self):
        """
            Create the periodic tasks launched by the TeSLA Worker Beat
        """
        from django_celery_beat.models import IntervalSchedule, PeriodicTask

        # Get task intervals
        providers_notification = 30

        # Send notifications to providers
        task_name = 'tesla_ce.tasks.notification.providers.send_provider_notifications'
        queue = self._config.config.get('CELERY_QUEUE_DEFAULT')
        try:
            interval = IntervalSchedule.objects.get(every=providers_notification, period=IntervalSchedule.SECONDS)
        except IntervalSchedule.DoesNotExist:
            interval = IntervalSchedule.objects.create(every=providers_notification, period=IntervalSchedule.SECONDS)
        PeriodicTask.objects.update_or_create(name=task_name, task=task_name, defaults={
            'enabled': 1,
            'interval': interval,
            'description': 'Send notifications to providers',
            'queue': queue
        })

