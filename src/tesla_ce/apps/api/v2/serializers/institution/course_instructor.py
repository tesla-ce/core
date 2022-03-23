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
"""Instructor api serialize module."""
from rest_framework import serializers
from rest_framework import validators

from tesla_ce.models import Institution
from tesla_ce.models import InstitutionUser
from tesla_ce.models import Instructor
from tesla_ce.models import User


class InstitutionCourseInstructorSerializer(serializers.ModelSerializer):
    """Instructor serialize model module."""
    username = serializers.CharField(read_only=True)
    uid = serializers.CharField()
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    institution_id = serializers.HiddenField(allow_null=True, default=None)
    course_id = serializers.HiddenField(allow_null=True, default=None)

    class Meta:
        model = Instructor
        exclude = ["password", "is_superuser", "is_staff", "is_active", "date_joined", "groups",
                   "user_permissions", "institution", "login_allowed", "inst_admin", "send_admin",
                   "data_admin", "legal_admin", "last_login", "locale"]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_vle__institution_id']
        attrs['course_id'] = self.context['view'].kwargs['parent_lookup_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
