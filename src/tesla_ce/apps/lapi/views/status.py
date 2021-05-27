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

from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from ..serializers import StatusSerializer
from ..utils import is_authenticated


class StatusView(APIView):
    """
        Provide an enrolment sample for a learner
    """
    def _get_path_status(self, path):
        if not default_storage.exists(path):
            return "NOT_FOUND", None
        if default_storage.exists('{}.error'.format(path)):
            return "ERROR", json.loads(default_storage.open('{}.error'.format(path),'r').read())
        if default_storage.exists('{}.valid'.format(path)):
            return "VALID", json.loads(default_storage.open('{}.valid'.format(path),'r').read())
        if default_storage.exists('{}.timeout'.format(path)):
            return "TIMEOUT", json.loads(default_storage.open('{}.timeout'.format(path),'r').read())
        return "PENDING", None

    def post(self, request, institution_id,  learner_id, format=None):
        serializer = StatusSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            if not is_authenticated(request, institution_id, learner_id, serializer.data):
                return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': "Invalid token"})

            status_response_list = []
            for path in serializer.data['samples']:
                path_status = self._get_path_status(path)
                status_response_list.append({
                    'sample': path,
                    'status': path_status[0],
                    'info': path_status[1]
                })

            return Response(status_response_list)

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})
