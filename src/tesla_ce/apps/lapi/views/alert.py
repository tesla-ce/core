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
""" Learner alert messages views module """
from django.utils import timezone

from tesla_ce import tasks
from .base import BaseLearnerAPIView
from ..serializers.alert import AlertMessageSerializer


class LearnerAlert(BaseLearnerAPIView):
    """
        Provide an alert message sample for a learner
    """
    serializer_class = AlertMessageSerializer

    def get_storing_path(self, institution_id, data):
        """
            Create the path where this sample should be stored
            :param institution_id: Id of the institution
            :type institution_id: int
            :param data: The data of the request
            :type data: dict
            :return: Path to the storage
            :rtype: str
        """
        prefix = timezone.now().strftime("%Y%m%d_%H%M%S_%f")
        if data.get('session_id') is not None:
            path = '{}/alerts/{}/{}/{}/sessions/{}/{}_{}'.format(
                institution_id,
                data['learner_id'],
                data['course_id'],
                data['activity_id'],
                data['session_id'],
                prefix,
                data['level'].upper()
            )
        else:
            path = '{}/alerts/{}/{}/{}/documents/{}_{}'.format(
                institution_id,
                data['learner_id'],
                data['course_id'],
                data['activity_id'],
                prefix,
                data['level'].upper()
            )

        return path

    def enqueue_request(self, data, path):
        """
            Enqueue a new task to manage new storage data
            :param data: Stored data
            :type data: dict
            :param path: Path where the data has been stored
            :type path: str
        """
        kwargs = {
            'level': data['level'],
            'activity_id': data['activity_id'],
            'learner_id': data['learner_id'],
            'path': path,
            'raised_at': data.get('raised_at'),
            'instruments': data.get('instruments'),
            'session_id': data.get('session_id')
        }
        tasks.requests.alerts.create_alert.apply_async(kwargs=kwargs)
