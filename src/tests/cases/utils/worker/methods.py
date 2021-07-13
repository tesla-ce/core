#  Copyright (c) 2021 Xavier Baró
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
""" TeSLA CE Worker actions for Use Case tests """
import mock


def get_task_by_queue(tasks):
    """
        Split a list of tasks on their respective queues
        :param tasks: List of tasks
        :return: Dictionary with tasks organized in queues
    """
    queues = {}
    for task in tasks:
        if task[2]['queue'] not in queues:
            queues[task[2]['queue']] = []
        queues[task[2]['queue']].append(task)
    return queues


def worker_validation_summary(tasks):
    """
    Worker compute validation summary from individual validations
    :param tasks: Pending tasks to be processed
    :return: List of new pending tasks
    """
    # List simulating the enrolment queue
    pending_tasks_enrolment = []

    def enrol_learner_test(*args, **kwargs):
        pending_tasks_enrolment.append(('enrol_learner', args, kwargs))

    # Run validation summary tasks
    with mock.patch('tesla_ce.tasks.requests.enrolment.enrol_learner.apply_async', enrol_learner_test):
        from tesla_ce.tasks.requests.enrolment import create_validation_summary
        for task in tasks:
            assert task[0] == 'create_validation_summary'
            create_validation_summary(*task[1][0])

    return pending_tasks_enrolment


def worker_enrol_learner(tasks):
    """
        Worker distribute enrolment tasks among providers
        :param tasks: List of pending tasks
        :return: List of tasks assigned to each provider
    """
    # List simulating the enrolment queue
    pending_tasks_enrolment = []

    def enrol_learner_test(*args, **kwargs):
        pending_tasks_enrolment.append(('enrol_learner', args, kwargs))

    # Run validation summary tasks
    with mock.patch('tesla_ce.tasks.requests.enrolment.enrol_learner.apply_async', enrol_learner_test):
        from tesla_ce.tasks.requests.enrolment import enrol_learner
        for task in tasks:
            assert task[0] == 'enrol_learner'
            enrol_learner(*task[1][0])

    return pending_tasks_enrolment


def worker_send_notifications():
    """
        Worker process notification tasks
        :return: List of pending provider notification tasks
    """
    # List simulating the notifications queue
    pending_tasks_notification = []

    def provider_notify_test(*args, **kwargs):
        pending_tasks_notification.append(('provider_notify', args, kwargs))

    # Process notifications
    with mock.patch('tesla_ce.tasks.notification.providers.provider_notify.apply_async',
                    provider_notify_test):
        from tesla_ce.tasks.notification.providers import send_provider_notifications
        send_provider_notifications()

    return pending_tasks_notification


def worker_create_reports(tasks):
    """
        Worker process verification results to create the reports
        :param tasks: List of pending reporting tasks
    """
    # List simulating the reporting queue
    pending_tasks_reporting = []

    # List simulating the reporting queue
    pending_tasks_reporting2 = []

    def update_learner_activity_instrument_report_test(*args, **kwargs):
        pending_tasks_reporting.append(('update_learner_activity_instrument_report', args, kwargs))

    def update_learner_activity_report_test(*args, **kwargs):
        pending_tasks_reporting2.append(('update_learner_activity_report', args, kwargs))

    for task in tasks:
        assert task[0] == 'create_verification_summary'
        with mock.patch(
                'tesla_ce.tasks.reports.results.update_learner_activity_instrument_report.apply_async',
                update_learner_activity_instrument_report_test):
            from tesla_ce.tasks.requests.verification import create_verification_summary
            create_verification_summary(*task[1][0])

    # Perform reporting tasks
    for task in pending_tasks_reporting:
        assert task[0] == 'update_learner_activity_instrument_report'
        with mock.patch(
                'tesla_ce.tasks.reports.results.update_learner_activity_report.apply_async',
                update_learner_activity_report_test):
            from tesla_ce.tasks.reports.results import update_learner_activity_instrument_report
            update_learner_activity_instrument_report(*task[1][0])

    # Perform reporting tasks
    for task in pending_tasks_reporting2:
        assert task[0] == 'update_learner_activity_report'
        from tesla_ce.tasks.reports.results import update_learner_activity_report
        from celery.exceptions import Reject
        try:
            update_learner_activity_report(*task[1][0])
        except Reject:
            # Raised when no new data is available
            pass
