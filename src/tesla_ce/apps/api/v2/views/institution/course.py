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
""" Course from a Course Group views module """
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionCourseSerializer
from tesla_ce.models import Course
from tesla_ce.models.user import is_global_admin
from tesla_ce.models.user import get_institution_user


# pylint: disable=too-many-ancestors
class InstitutionCourseViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows course in a vle to be viewed or edited.
    """
    model = Course
    serializer_class = InstitutionCourseSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    permission_classes = [
        permissions.InstitutionMemberReadOnlyPermission |
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminPermission
    ]
    # filterset_fields = ['code', 'vle_course_id', 'description', 'vle']
    # search_fields = ['vle_course_id', 'description', 'code', 'vle']

    def get_queryset(self):
        # Except for global admins, and institution admins and data admins, returns only the courses where the user is
        # involved as instructor or learner
        qs = super().filter_queryset_by_parents_lookups(Course.objects)
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            if not inst_user.inst_admin and not inst_user.data_admin:
                qs = qs.filter(
                    Q(instructors__id=inst_user.id) | Q(learners__id=inst_user.id)
                ).distinct()
        return qs.all()
