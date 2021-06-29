#  Copyright (c) 2020 Roger Muñoz
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
""" ActivityInstrument views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLECourseActivityInstrumentSerializer
from tesla_ce.models import ActivityInstrument


# pylint: disable=too-many-ancestors
class VLECourseActivityInstrumentViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows activity instruments to be viewed or edited.
    """
    serializer_class = VLECourseActivityInstrumentSerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['instrument_id']
    search_fields = ['instrument_id']

    def get_queryset(self):
        queryset = ActivityInstrument.objects
        if self.kwargs['parent_lookup_activity_id']:
            queryset = queryset.filter(
                activity_id=self.kwargs['parent_lookup_activity_id']
            )
        return queryset.all().order_by('id')
