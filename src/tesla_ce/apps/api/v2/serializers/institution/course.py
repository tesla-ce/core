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
""" Course api serialize module """
from rest_framework import serializers

from tesla_ce.models import Course
from ..vle import VLESerializer


class InstitutionCourseSerializer(serializers.ModelSerializer):
    """Course serialize class."""

    id = serializers.IntegerField()
    vle = VLESerializer(read_only=True)
    vle_course_id = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    start = serializers.DateTimeField(read_only=True)
    end = serializers.DateTimeField(read_only=True)
    user_roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        exclude = ["learners", "instructors"]

    def get_user_roles(self, instance):
        """
            Get the list of roles for a user in this course
            :param instance: Course instance
            :return: List of roles
        """
        roles = []
        if instance.learners.filter(id=self.context['request'].user.id).count() > 0:
            roles.append('LEARNER')
        if instance.instructors.filter(id=self.context['request'].user.id).count() > 0:
            roles.append('INSTRUCTOR')
        return roles
