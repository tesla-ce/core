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
from tesla_ce import models
from tesla_ce import tasks


class Command(TeslaDeployCommand):
    """ Command to resend all pending requests """
    help = 'Resend all pending requests'
    requires_system_checks = '__all__'

    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        # Set default arguments
        super().add_arguments(parser)

        parser.add_argument(
            '--course-id',
            help='Course Id',
            default=None,
        )

        parser.add_argument(
            '--activity-id',
            help='Activity Id',
            default=None,
        )

        parser.add_argument(
            '--institution-id',
            help='Institution Id',
            default=None,
        )

        parser.add_argument(
            '--user-id',
            help='User Id',
            default=None,
        )

        parser.add_argument(
            '--include-processed',
            action='store_true',
            help='Resend also processed requests',
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """
        # Get all requests
        requests = models.Request.objects

        # Filter by institution
        if self._options['institution_id'] is not None:
            requests = requests.filter(learner__institution_id=self._options['institution_id'])

        # Filter by user
        if self._options['user_id'] is not None:
            requests = requests.filter(learner_id=self._options['user_id'])

        # Filter by course
        if self._options['course_id'] is not None:
            requests = requests.filter(activity__course_id=self._options['course_id'])

        # Filter by activity
        if self._options['activity_id'] is not None:
            requests = requests.filter(activity_id=self._options['activity_id'])

        # Filter processed
        if not self._options['include_processed']:
            requests = requests.filter(status__in=[0, 1, 2, 5, 6])  # Valid and error samples are not included

        requests_count = 0
        error_count = 0
        for request in requests.all():
            try:
                tasks.requests.verification.verify_request(request.id)
            except Exception:
                error_count += 1
            requests_count += 1

        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('{} requests sent'.format(requests_count)))
        else:
            self.stdout.write(self.style.ERROR('{} requests sent with {} errors'.format(requests_count, error_count)))
