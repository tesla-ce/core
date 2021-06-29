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
""" Course views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLECourseSerializer
from tesla_ce.models import Course


# pylint: disable=too-many-ancestors
class VLECourseViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows course in a vle to be viewed or edited.
    """
    model = Course
    serializer_class = VLECourseSerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['code', 'vle_course_id', 'description', 'vle']
    search_fields = ['vle_course_id', 'description', 'code', 'vle']

    def get_queryset(self):
        queryset = Course.objects
        if 'vle_id' in self.kwargs:
            queryset = queryset.filter(
                vle_id=self.kwargs['parent_lookup_vle_id']
            )
        return queryset.all().order_by('id')
