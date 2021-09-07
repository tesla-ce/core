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
    """ Command to resend all pending enrolment samples """
    help = 'Resend all pending enrolment samples'
    requires_system_checks = '__all__'

    def add_arguments(self, parser):
        """
            Define custom arguments for this command

            :param parser: Input command parser instance
        """
        # Set default arguments
        super().add_arguments(parser)

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
            help='Resend also processed samples',
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """
        # Get all samples
        samples = models.EnrolmentSample.objects

        # Filter by institution
        if self._options['institution_id'] is not None:
            samples = samples.filter(learner__institution_id=self._options['institution_id'])

        # Filter by user
        if self._options['user_id'] is not None:
            samples = samples.filter(learner_id=self._options['user_id'])

        # Filter processed
        if not self._options['include_processed']:
            samples = samples.filter(status__in=[0, 3, 4])  # Valid and error samples are not included

        samples_count = 0
        error_count = 0
        for sample in samples.all():
            try:
                tasks.requests.enrolment.validate_request(sample.learner_id, sample.id)
            except Exception:
                error_count += 1
            samples_count += 1

        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('{} samples sent'.format(samples_count)))
        else:
            self.stdout.write(self.style.ERROR('{} samples sent with {} errors'.format(samples_count, error_count)))
