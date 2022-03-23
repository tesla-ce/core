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
    """ Command to rebuild all reports """
    help = 'Rebuild all reports'
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
            '--institution-id',
            help='Institution Id',
            default=None,
        )

        parser.add_argument(
            '--user-id',
            help='User Id',
            default=None,
        )

    def custom_handle(self):
        """
            Custom actions for this command
        """
        # Get all activities
        activities = models.Activity.objects

        # Filter by institution
        if self._options['institution_id'] is not None:
            activities = activities.filter(vle__institution_id=self._options['institution_id'])

        # Filter by course
        if self._options['course_id'] is not None:
            activities = activities.filter(course_id=self._options['course_id'])

        report_count = 0
        error_count = 0
        for activity in activities.all():
            learners = activity.course.learners
            if self._options['user_id'] is not None:
                learners = learners.filter(id=self._options['user_id'])
            for learner in learners.all():
                try:
                    tasks.reports.update_learner_activity_report(learner.id, activity.id, force_update=True)
                except Exception:
                    error_count += 1
                report_count += 1

        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('{} reports generated'.format(report_count)))
        else:
            self.stdout.write(self.style.ERROR('{} reports generated with {} errors'.format(report_count, error_count)))
