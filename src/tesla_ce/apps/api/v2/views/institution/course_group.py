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
""" Course Group views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api.v2.serializers import InstitutionCourseGroupSerializer
from tesla_ce.apps.api.v2.serializers import VLECourseSerializer
from tesla_ce.models import Course
from tesla_ce.models import CourseGroup


# pylint: disable=too-many-ancestors
class InstitutionCourseGroupViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows course groups to be viewed or edited.
    """
    model = CourseGroup
    serializer_class = InstitutionCourseGroupSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    def get_queryset(self):
        queryset = CourseGroup.objects
        if 'parent_lookup_institution_id' in self.kwargs:
            queryset = queryset.filter(
                institution_id=self.kwargs['parent_lookup_institution_id']
            )
        return queryset.all().order_by('id')


# pylint: disable=too-many-ancestors
class InstitutionCourseGroupCourseViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows courses in course groups to be added or deleted.
    """
    model = Course
    serializer_class = VLECourseSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    '''
    filterset_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    search_fields = ['activity_type', 'external_token', 'description', 'conf', 'vle']
    '''

    def get_queryset(self):
        queryset = CourseGroup.objects
        if 'parent_lookup_institution_id' in self.kwargs:
            queryset = queryset.filter(
                institution_id=self.kwargs['parent_lookup_institution_id']
            )
        return queryset.all().order_by('id')
