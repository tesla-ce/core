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
""" VLE Course Learner views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLECourseInstructorSerializer
from tesla_ce.models import Course
from tesla_ce.models import Instructor


# pylint: disable=too-many-ancestors
class VLECourseInstructorViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows activity to be viewed or edited.
    """
    model = Instructor
    serializer_class = VLECourseInstructorSerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['uid', 'email', 'first_name', 'last_name']
    search_fields = ['uid', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        if 'parent_lookup_vle_id' in self.kwargs and 'parent_lookup_course_id' in self.kwargs:
            course = Course.objects.get(id=self.kwargs['parent_lookup_course_id'])
            queryset = course.instructors
        else:
            queryset = Instructor.objects
        return queryset.all().order_by('id')

    def perform_destroy(self, instance):
        """
            Remove an instructor from current course
            :param instance: Instructor to be removed
        """
        course = Course.objects.get(id=self.kwargs['parent_lookup_course_id'])
        course.instructors.remove(instance)
