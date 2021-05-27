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
""" Learner enrolment samples views module """
from django.utils import timezone

from tesla_ce import tasks
from .base import BaseLearnerAPIView
from ..serializers.enrolment import EnrolmentSampleSerializer


class LearnerEnrolment(BaseLearnerAPIView):
    """
        Provide an enrolment sample for a learner
    """
    serializer_class = EnrolmentSampleSerializer

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
        metadata = data.get('metadata')
        if metadata is not None and 'filename' in metadata:
            filename = metadata.get('filename', 'document')
        else:
            filename = 'request'

        path = '{}/enrolment/{}/samples/{}_{}'.format(
            institution_id,
            data['learner_id'],
            prefix,
            filename)

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
            'learner_id': data['learner_id'],
            'path': path,
            'instruments': data['instruments']
        }
        tasks.requests.enrolment.create_sample.apply_async(kwargs=kwargs)
