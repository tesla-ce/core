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
import json

import botocore
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from tesla_ce.lib.exception import tesla_report_exception
from ..utils import is_authenticated


class BaseLearnerAPIView(APIView):
    """
        Base class for Learner API views
    """
    serializer_class = None

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
        raise NotImplementedError('This method must be implemented')

    def enqueue_request(self, data, path):
        """
            Enqueue a new task to manage new storage data
            :param data: Stored data
            :type data: dict
            :param path: Path where the data has been stored
            :type path: str
        """
        raise NotImplementedError('This method must be implemented')

    def post(self, request, institution_id, learner_id, format=None):
        """
            Perform data storage
            :param request: The received request
            :param institution_id: Institution unique ID
            :param learner_id: Learner ID in TeSLA
            :param format: Format of the request
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        try:
            if serializer.is_valid():
                # Check that provided token is compatible with the data
                if not is_authenticated(request, institution_id, learner_id, serializer.data):
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'status': "ERROR", 'errors': "Invalid token"})
                # Generate the target path for the request
                path = self.get_storing_path(institution_id, serializer.data)
                # Store the request
                resp = default_storage.save(path, ContentFile(json.dumps(serializer.data).encode('utf-8')))
                # Notify the new stored request
                self.enqueue_request(serializer.data, resp)

                return Response({"status": "OK", "path": resp})

            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"status": "ERROR", 'errors': serializer.errors},
                            content_type="application/json")
        except botocore.exceptions.ClientError as cli_err:
            tesla_report_exception(cli_err)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"status": "ERROR", 'errors': cli_err.response},
                            content_type="application/json")

        except Exception as ex:
            tesla_report_exception(ex)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"status": "ERROR", 'errors': ex},
                            content_type="application/json")
