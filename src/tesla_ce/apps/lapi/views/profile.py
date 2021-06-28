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
""" Learner profile views module """
import json

from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from tesla_ce.models import AuthenticatedUser
from tesla_ce.models import Learner
from tesla_ce.models import InstitutionUser

from tesla_ce.lib.exception import tesla_report_exception

from ..utils import is_authenticated
from ..serializers import ProfileSerializer


class ProfileView(APIView):
    """
        Base class for Learner API views
    """
    serializer_class = ProfileSerializer

    def get(self, request, institution_id, learner_id):
        """
            Get learner profile
            :param request: The received request
            :param institution_id: Institution unique ID
            :param learner_id: Learner ID in TeSLA
        """
        try:
            # Check that provided token is compatible with the data
            if not is_authenticated(request, institution_id, learner_id, {'learner_id': str(learner_id)}):
                return Response(status=status.HTTP_403_FORBIDDEN, data={'status': "ERROR", 'errors': "Invalid token"})
            if isinstance(request.user, AuthenticatedUser):
                return Response(status=status.HTTP_403_FORBIDDEN,
                                data={'status': "OK", 'profile': {
                                   'learner_id': str(learner_id)
                                }})
            if isinstance(request.user, Learner):
                return Response(ProfileSerializer(request.user).data)
            if isinstance(request.user, InstitutionUser):
                return Response(ProfileSerializer(request.user.learner).data)

            return Response(status=status.HTTP_403_FORBIDDEN, data={'status': "ERROR", 'errors': "Invalid user object"})

        except Exception as ex:
            tesla_report_exception(ex)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            data={"status": "ERROR", 'errors': ex},
                            content_type="application/json")
