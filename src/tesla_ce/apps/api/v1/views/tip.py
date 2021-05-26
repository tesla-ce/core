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
""" API Views for TeSLA Identity Provieder (TIP) """
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from tesla_ce.models import Institution
from tesla_ce.models import Learner
from ..serializers.tip import LearnerIdSerializer
from ..serializers.tip import LearnerSerializer
from ..serializers.tip import MultipleLearnerIdSerializer


class LearnerId(APIView):
    """
        Get the Learner TeSLA Id from mail
    """
    def post(self, request, format=None):

        serializer = LearnerIdSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Use default institution
            try:
                institution = Institution.objects.get(pk=1)
            except Institution.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            # Search for the learner
            try:
                learner = Learner.objects.get(institution=institution, email=serializer.validated_data['mail'])
            except Learner.DoesNotExist:
                learner = Learner.objects.create(uid=serializer.validated_data['mail'],
                                                 email=serializer.validated_data['mail'],
                                                 username=serializer.validated_data['mail'],
                                                 institution=institution)
            return Response(LearnerSerializer(learner).data)

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})


class MultipleLearnerId(APIView):
    """
        Get the Learner TeSLA Ids from a list of mails
    """
    def post(self, request, format=None):
        serializer = MultipleLearnerIdSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Use default institution
            try:
                institution = Institution.objects.get(pk=1)
            except Institution.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            # Search for the learners
            learners = Learner.objects.filter(institution=institution,
                                              email__in=serializer.validated_data['mails']
                                              ).all()
            return Response(LearnerSerializer(learners, many=True).data)

        return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': serializer.errors})
