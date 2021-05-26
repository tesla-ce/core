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
#
""" Provider views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import ProviderSerializer
from tesla_ce.models import Provider


# pylint: disable=too-many-ancestors
class AdminProviderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows instrument provider to be viewed or edited.
    """
    model = Provider
    serializer_class = ProviderSerializer
    permission_classes = [permissions.GlobalAdminPermission]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    def get_queryset(self):
        queryset = Provider.objects
        if 'parent_lookup_instrument_id' in self.kwargs:
            queryset = queryset.filter(
                instrument_id=self.kwargs['parent_lookup_instrument_id']
            )
        return queryset.all().order_by('id')
