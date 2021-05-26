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
""" API Views for TeSLA eAssessment Portal (TEP) """
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from tesla_ce import get_default_client
from tesla_ce.apps.api.auth.serializers import AuthTokenPairSerializer
from tesla_ce.models import Institution
from tesla_ce.models import Learner
from ..serializers.tep import LearnerEnrolment


class LearnerEnrolmentView(APIView):
    """
        Get enrolment data
    """
    def get(self, request, learner_id, format=None):
        # Use default institution
        try:
            institution = Institution.objects.get(pk=1)
        except Institution.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # Search for the learner
        try:
            learner = Learner.objects.get(institution=institution, learner_id=learner_id)
        except Learner.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(LearnerEnrolment(learner).data)


class LearnerEnrolmentTokenView(APIView):
    """
        Get enrolment token
    """
    def get(self, request, learner_id, format=None):
        # Use default institution
        try:
            institution = Institution.objects.get(pk=1)
        except Institution.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # Search for the learner
        try:
            learner = Learner.objects.get(institution=institution, learner_id=learner_id)
        except Learner.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        tokens = get_default_client().get_learner_token_pair(learner, ['/lapi/v1/enrolment/*'])

        return Response(AuthTokenPairSerializer(tokens).data)
