#  Copyright (c) 2020 Roger Muñoz
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
from .vle import VLESerializer


class VLECourseSerializer(serializers.ModelSerializer):
    """Course serialize class."""

    vle = VLESerializer(read_only=True)
    vle_id = serializers.HiddenField(default=None, allow_null=True)

    class Meta:
        model = Course
        exclude = ["learners", "instructors",]
        validators = [serializers.UniqueTogetherValidator(
            queryset=Course.objects.all(),
            fields=['vle_id', 'vle_course_id']
        ), ]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['vle_id'] = self.context['view'].kwargs['parent_lookup_vle_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
