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
""" CourseGroup api serialize module."""
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from tesla_ce.models import Course
from tesla_ce.models import CourseGroup
from .institution import InstitutionSerializer
from ..vle import VLESerializer


class InstitutionCourseGroupsField(serializers.PrimaryKeyRelatedField):
    """ Related Institution field"""
    def get_queryset(self):
        """
            Return the queryset for this field
            :return: Queryset
        """
        queryset = super().get_queryset()
        if 'parent_lookup_institution_id' in self.context['view'].kwargs:
            queryset = queryset.filter(institution_id=self.context['view'].kwargs['parent_lookup_institution_id'])
        if self.root.instance is not None:
            queryset = queryset.exclude(id=self.root.instance.id)
        return queryset


class InstitutionCourseGroupSerializer(serializers.ModelSerializer):
    """CourseGroup serialize model module."""

    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.HiddenField(default=None, allow_null=True)
    parent = InstitutionCourseGroupsField(allow_null=True, default=None,
                                          queryset=CourseGroup.objects)

    class Meta:
        model = CourseGroup
        exclude = ["courses"]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_institution_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)


class InstitutionCourseGroupCourseSerializer(serializers.ModelSerializer):
    """Course serialize class."""

    id = serializers.IntegerField()
    vle_id = serializers.IntegerField(read_only=True)
    vle_course_id = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Course
        exclude = ["learners", "instructors", "vle"]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['group_id'] = self.context['view'].kwargs['parent_lookup_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)

    def create(self, validated_data):
        """
            Add the course to the group and return the related course

            :param validated_data: Valid data from request
            :return: Course
        """
        try:
            group = CourseGroup.objects.get(id=validated_data['group_id'])
        except CourseGroup.DoesNotExist:
            raise NotFound('Course Group not found')
        try:
            course = Course.objects.get(id=validated_data['id'])
        except Course.DoesNotExist:
            raise NotFound('Course not found')
        group.courses.add(course)

        return course
