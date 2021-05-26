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
""" Institution views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionAdminSerializer
from tesla_ce.models import Institution


# pylint: disable=too-many-ancestors
class InstitutionAdminViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows institution to be viewed or edited.
    """
    model = Institution
    queryset = Institution.objects.all().order_by('created_at')
    serializer_class = InstitutionAdminSerializer
    permission_classes = [permissions.GlobalAdminPermission]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    lookup_url_kwarg = 'institution_id'
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''
