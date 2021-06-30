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
""" Provider sample validation views module """
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.views import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import (
    ProviderEnrolmentSampleValidationSerializer
)
from tesla_ce.models import EnrolmentSampleValidation


# pylint: disable=too-many-ancestors
class ProviderEnrolmentSampleValidationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Provider manage enrolment sample validation.
    """
    queryset = EnrolmentSampleValidation.objects
    serializer_class = ProviderEnrolmentSampleValidationSerializer
    permission_classes = [
        permissions.ProviderPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    @action(detail=True, methods=['POST'])
    def status(self, request, *args, **kwargs):
        """
            Change enrolment sample validation status
        """
        status = request.data.get('status')
        if status is None:
            raise ValidationError('status field is required')
        try:
            status = int(status)
        except:
            raise ValidationError('status must be an integer')

        if status < 0 or status > 4:
            raise ValidationError('status value out of range')

        sample_validation = get_object_or_404(self.queryset,
                                              provider_id=kwargs['parent_lookup_provider_id'],
                                              pk=kwargs['pk'])

        sample_validation.status = status
        sample_validation.save()
        return Response(self.serializer_class(instance=sample_validation).data)
