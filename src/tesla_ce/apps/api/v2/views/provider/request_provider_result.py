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
""" RequestResult views module """
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.views import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import ProviderVerificationRequestResultSerializer
from tesla_ce.models import RequestProviderResult


# pylint: disable=too-many-ancestors
class ProviderVerificationRequestResultViewSet(NestedViewSetMixin, UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows activity to be viewed or edited.
    """
    queryset = RequestProviderResult.objects
    lookup_field = 'request_id'
    serializer_class = ProviderVerificationRequestResultSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    permission_classes = [
        permissions.ProviderPermission
    ]
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

        if status < 0 or status > 7:
            raise ValidationError('status value out of range')

        request_result = get_object_or_404(self.queryset,
                                           provider_id=kwargs['parent_lookup_provider_id'],
                                           request_id=kwargs['request_id'])

        if request_result.status == 1:
            raise ValidationError('Cannot change processed results status.')

        request_result.status = status
        request_result.save()

        return Response(self.serializer_class(instance=request_result).data)
