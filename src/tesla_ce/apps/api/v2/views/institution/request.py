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
""" Request views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionCourseActivityReportRequestSerializer
from tesla_ce.models import Request
from tesla_ce.models import ReportActivity


# pylint: disable=too-many-ancestors
class InstitutionCourseActivityReportRequestViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows activity to be viewed or edited.
    """
    serializer_class = InstitutionCourseActivityReportRequestSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminReadOnlyPermission |
        permissions.InstitutionLearnerReadOnlyPermission |
        permissions.InstitutionCourseInstructorReadOnlyPermission
    ]
    filterset_fields = ['instruments']
    search_fields = ['instruments']

    def get_queryset(self):
        report = self.filter_queryset_by_parents_lookups(ReportActivity.objects).get()
        queryset = Request.objects.filter(activity=report.activity, learner=report.learner)
        return queryset.all().order_by('session_id', 'id')

