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
from tesla_ce.apps.api.v2.serializers import InstitutionCourseActivitySerializer
from tesla_ce.models import Activity


# pylint: disable=too-many-ancestors
class InstitutionCourseActivityViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows activity in a course to be viewed or edited.
    """
    model = Activity
    serializer_class = InstitutionCourseActivitySerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminPermission |
        permissions.InstitutionCourseInstructorPermission |
        permissions.InstitutionCourseLearnerReadOnlyPermission
    ]
    # filterset_fields = ['vle_id', 'vle_activity_type', 'vle_activity_id', 'course_id', 'name']
    # search_fields = ['vle_id', 'vle_activity_type', 'vle_activity_id', 'course_id', 'name']

    def get_queryset(self):
        queryset = self.filter_queryset_by_parents_lookups(Activity.objects)

        return queryset
