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
""" Celery client module """
from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings
from kombu import Exchange
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tesla_ce.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Production')

import configurations
configurations.setup()

app = Celery('tesla_ce')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Set queues to consume from
task_queues = tuple()
queues = []

if settings.TESLA_CONFIG.config.get('CELERY_QUEUES') is None or len(
        settings.TESLA_CONFIG.config.get('CELERY_QUEUES')
) == 0:
    # Set the default queue
    app.conf.task_default_queue = settings.TESLA_CONFIG.config.get('CELERY_QUEUE_DEFAULT')
elif len(settings.TESLA_CONFIG.config.get('CELERY_QUEUES')) == 1:
    if settings.TESLA_CONFIG.config.get('CELERY_QUEUES')[0] == '__all__':
        queues = [
            'ENROLMENT', 'ENROLMENT_STORAGE', 'ENROLMENT_VALIDATION', 'VERIFICATION',
            'ALERTS', 'REPORTING'
        ]
    else:
        # Set the default queue
        queue = settings.TESLA_CONFIG.config.get('CELERY_QUEUES')[0]
        app.conf.task_default_queue = settings.TESLA_CONFIG.config.get('CELERY_QUEUE_{}'.format(queue.upper()))
else:
    queues = settings.TESLA_CONFIG.config.get('CELERY_QUEUES')

if len(queues) > 0:
    queue_list = tuple()
    with app.broker_connection() as connection:
        channel = connection.default_channel
        for queue in queues:
            queue_name = settings.TESLA_CONFIG.config.get('CELERY_QUEUE_{}'.format(queue.upper()))
            new_queue = Queue(queue_name,
                              exchange=Exchange(queue_name, type='direct', connection=connection),
                              routing_key=queue_name)
            new_queue(channel).declare()
            queue_list += (new_queue, )
    app.conf.task_queues = queue_list

# Set routing
app.conf.task_routes = ([
    ('tesla_ce.tasks.requests.enrolment.create_sample', {
        'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_ENROLMENT_STORAGE')}
    ),
    ('tesla_ce.tasks.requests.enrolment.validate_request', {
        'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_ENROLMENT_VALIDATION')}
    ),
    ('tesla_ce.tasks.requests.enrolment.create_validation_summary', {
        'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_ENROLMENT_VALIDATION')}
    ),
    ('tesla_ce.tasks.requests.enrolment.enrol_learner', {
       'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_ENROLMENT')}
    ),
    ('tesla_ce.tasks.requests.verification.*', {
        'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_VERIFICATION')
    }),
    ('tesla_ce.tasks.requests.alerts.*', {'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_ALERTS')}),
    ('tesla_ce.tasks.reports.*', {'queue': settings.TESLA_CONFIG.config.get('CELERY_QUEUE_REPORTING')}),
],)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
