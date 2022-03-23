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
from django.shortcuts import get_object_or_404

from django_filters import rest_framework as filters_dj

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api.v2.serializers import InstitutionCourseGroupSerializer
from tesla_ce.apps.api.v2.serializers import InstitutionCourseGroupCourseSerializer
from tesla_ce.models import Course
from tesla_ce.models import CourseGroup

def groups_values():
    groups = CourseGroup.objects.all()
    return ((group.id, group) for group in groups)


class GroupFilter(filters_dj.FilterSet):
    parent = filters_dj.ChoiceFilter(field_name="parent",
                                     label="parent",
                                     choices=groups_values,
                                     null_label='None',
                                     null_value=-1,
                                     method='filter_parent')

    name = filters_dj.CharFilter(lookup_expr='icontains')
    description = filters_dj.CharFilter(lookup_expr='icontains')

    def filter_parent(self, queryset, name, value):

        # In case value is not a valid integer, ignore the filter
        try:
            value = int(value)
        except ValueError:
            return queryset

        # Request users with no institution assigned
        if value < 0:
            return queryset.filter(parent=None)

        # Filter by provided institution
        return queryset.filter(parent_id=value)

    class Meta:
        model = CourseGroup
        fields = ['name', 'description', 'parent']


# pylint: disable=too-many-ancestors
class InstitutionCourseGroupViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows course groups to be viewed or edited.
    """
    model = CourseGroup
    serializer_class = InstitutionCourseGroupSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['parent', 'name', 'description']
    filterset_class = GroupFilter

    def get_queryset(self):
        queryset = super().filter_queryset_by_parents_lookups(CourseGroup.objects)
        return queryset.all().order_by('id')


# pylint: disable=too-many-ancestors
class InstitutionCourseGroupCourseViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows courses in course groups to be added or deleted.
    """
    model = Course
    serializer_class = InstitutionCourseGroupCourseSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['vle_id', 'vle_course_id', 'description', 'code', 'start', 'end']

    def get_queryset(self):
        """
            Get the queryset for this view
            :return: Queryset
        """
        group = get_object_or_404(super().filter_queryset_by_parents_lookups(CourseGroup.objects))
        return group.courses.all().order_by('id')

    def perform_destroy(self, instance):
        """
            Remove the course from the group
            :param instance: Course
        """
        group = get_object_or_404(super().filter_queryset_by_parents_lookups(CourseGroup.objects))
        group.courses.remove(instance)
