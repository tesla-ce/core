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
""" Institution Course Learner views module """
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import InstitutionLearnerDetailSerializer
from tesla_ce.apps.api.v2.serializers import InstitutionCourseLearnerSerializer

from tesla_ce.models import Course
from tesla_ce.models import Learner
from tesla_ce.models.user import get_institution_user
from tesla_ce.models.user import is_global_admin


# pylint: disable=too-many-ancestors
class InstitutionCourseLearnerViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows course learners to be viewed or edited.
    """
    model = Learner
    serializer_class = InstitutionCourseLearnerSerializer
    serializer_detail_class = InstitutionLearnerDetailSerializer
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminPermission |
        permissions.InstitutionDataAdminReadOnlyPermission |
        permissions.InstitutionCourseInstructorPermission |
        permissions.InstitutionCourseLearnerReadOnlyPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['uid', 'email', 'first_name', 'last_name']
    search_fields = ['uid', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        queryset = self.filter_queryset_by_parents_lookups(Course.objects)
        queryset = queryset.get().learners
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            try:
                is_instructor = inst_user.instructior in queryset.get().instructors.all()
            except Exception:
                is_instructor = False
            if not inst_user.inst_admin and not inst_user.legal_admin and not inst_user.data_admin and not is_instructor:
                queryset = queryset.filter(id=inst_user.id)
        return queryset.all().order_by('id')
