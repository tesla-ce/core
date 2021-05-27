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
"""User api serialize module."""
from rest_framework import serializers
from rest_framework import validators

from tesla_ce.models import User


class UserSerializer(serializers.ModelSerializer):
    """User serialize model module."""

    username = serializers.CharField(allow_blank=False,
                                     allow_null=False,
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
    password = serializers.CharField(write_only=True, default=None)
    institution = serializers.SerializerMethodField(read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'

    def get_institution(self, object):
        if hasattr(object, "institutionuser"):
            roles = []
            if hasattr(object.institutionuser, "instructor"):
                roles.append("INSTRUCTOR")
            if hasattr(object.institutionuser, "learner"):
                roles.append("LEARNER")
            if object.institutionuser.inst_admin:
                roles.append("ADMIN")
            if object.institutionuser.send_admin:
                roles.append("SEND")
            if object.institutionuser.legal_admin:
                roles.append("LEGAL")

            return {
                "id": object.institutionuser.institution.id,
                "acronym": object.institutionuser.institution.acronym,
                "uid": object.institutionuser.uid,
                "roles": roles,
                "locale": object.institutionuser.locale,
            }

        return None

    def get_roles(self, object):
        roles = []
        inst = self.get_institution(object)
        if inst is not None:
            roles = inst['roles']
        if object.is_staff:
            roles.append('GLOBAL_ADMIN')

        return roles
