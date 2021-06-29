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
from django.db.models import Subquery
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api import permissions
from tesla_ce.apps.api.v2.serializers import VLECourseActivityLearnerSerializer
from tesla_ce.apps.api.v2.serializers import VLECourseLearnerSerializer
from tesla_ce.models import Course
from tesla_ce.models import Learner


# pylint: disable=too-many-ancestors
class VLECourseLearnerViewSet(viewsets.ModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows learners in a course to be viewed or edited.
    """
    model = Learner
    serializer_class = VLECourseLearnerSerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['uid', 'email', 'first_name', 'last_name', 'learner_id']
    search_fields = ['uid', 'email', 'first_name', 'last_name', 'learner_id']

    def get_queryset(self):
        if 'parent_lookup_vle_id' in self.kwargs and 'parent_lookup_course_id' in self.kwargs:
            course = Course.objects.get(id=self.kwargs['parent_lookup_course_id'])
            queryset = course.learners
        else:
            queryset = Learner.objects
        return queryset.all().order_by('id')

    def perform_destroy(self, instance):
        """
            Remove a learner from current course
            :param instance: Learner to be removed
        """
        course = Course.objects.get(id=self.kwargs['parent_lookup_course_id'])
        course.learners.remove(instance)


# pylint: disable=too-many-ancestors
class VLECourseActivityLearnerViewSet(viewsets.ReadOnlyModelViewSet, NestedViewSetMixin):
    """
    API endpoint that allows access results for learners in a activity.
    """
    model = Learner
    serializer_class = VLECourseActivityLearnerSerializer
    permission_classes = [
        permissions.VLEPermission
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['uid', 'email', 'first_name', 'last_name', 'learner_id']
    search_fields = ['uid', 'email', 'first_name', 'last_name', 'learner_id']

    def get_queryset(self):
        if 'parent_lookup_vle_id' in self.kwargs and 'parent_lookup_course_id' in self.kwargs:
            queryset = Learner.objects.filter(id__in=Subquery(
                Learner.objects.filter(request__activity_id=1).values('id').all()
            ))
        else:
            queryset = Learner.objects
        return queryset.all().order_by('id')
