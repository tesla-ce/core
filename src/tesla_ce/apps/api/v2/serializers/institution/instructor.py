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

from tesla_ce.models import InstitutionUser
from tesla_ce.models import Instructor
from tesla_ce.models import User


class InstitutionInstructorSerializer(serializers.ModelSerializer):
    """Instructor serialize model module."""
    username = serializers.CharField(read_only=True,
                                     validators=[
                                         validators.UniqueValidator(queryset=User.objects.all())
                                     ]
                                     )
    last_login = serializers.DateTimeField(read_only=True)
    first_name = serializers.CharField(required=False, default=None)
    last_name = serializers.CharField(required=False, default=None)
    email = serializers.EmailField(required=False, default=None,
                                   validators=[
                                       validators.UniqueValidator(queryset=User.objects.all())
                                   ]
                                   )
    institution_id = serializers.HiddenField(default=None)

    class Meta:
        model = Instructor
        exclude = ["password", "is_superuser", "is_staff", "is_active", "date_joined", "groups",
                   "user_permissions", "institution", "login_allowed"]
        validators = [serializers.UniqueTogetherValidator(
            queryset=InstitutionUser.objects.all(),
            fields=['institution_id', 'uid']
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
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_institution_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
