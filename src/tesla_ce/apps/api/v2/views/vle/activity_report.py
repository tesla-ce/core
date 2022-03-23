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
""" Activity Report views module """
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLECourseActivityReportExtendedSerializer
from tesla_ce.apps.api.v2.serializers import VLECourseActivityReportSerializer
from tesla_ce.models import ReportActivity


# pylint: disable=too-many-ancestors
class VLECourseActivityReportViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows view activity reports.
    """
    model = ReportActivity
    queryset = ReportActivity.objects
    serializer_class = VLECourseActivityReportSerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    serializer_detail_class = VLECourseActivityReportExtendedSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['learner__first_name', 'learner__last_name', 'learner__email',
                     'identity_level', 'authorship_level', 'cheating_level']
