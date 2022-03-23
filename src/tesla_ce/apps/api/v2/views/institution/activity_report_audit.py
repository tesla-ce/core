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
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionCourseActivityReportAuditSerializer

from tesla_ce.models import Course
from tesla_ce.models import ReportActivityInstrument
from tesla_ce.models.user import get_institution_user
from tesla_ce.models.user import is_global_admin


# pylint: disable=too-many-ancestors
class InstitutionCourseActivityReportAuditViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows view activity report audit data.
    """
    model = ReportActivityInstrument
    serializer_class = InstitutionCourseActivityReportAuditSerializer
    lookup_field = 'instrument_id'
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminReadOnlyPermission |
        permissions.InstitutionDataAdminReadOnlyPermission |
        permissions.InstitutionCourseInstructorReadOnlyPermission |
        permissions.InstitutionCourseLearnerReadOnlyPermission
    ]

    def get_queryset(self):
        queryset = self.filter_queryset_by_parents_lookups(ReportActivityInstrument.objects)
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            if not inst_user.inst_admin and not inst_user.legal_admin and not inst_user.data_admin:
                course = Course.objects.get(
                    vle__institution=self.kwargs['parent_lookup_report__activity__vle__institution_id'],
                    id=self.kwargs['parent_lookup_report__activity__course_id']
                )
                try:
                    is_instructor = self.request.user.instructor in course.instructors.all()
                except Exception:
                    is_instructor = False
                if not is_instructor:
                    if not inst_user.institution.allow_learner_report or not inst_user.institution.allow_learner_audit:
                        raise exceptions.PermissionDenied('Not allowed')
                    queryset = queryset.filter(report__learner_id=inst_user.id)
        return queryset.all()
