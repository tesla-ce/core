#  Copyright (c) 2021 Xavier Baró
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
""" Learner profile Serializer """
from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    """ Body serializer for alert messages."""

    learner_id = serializers.UUIDField(required=True, allow_null=False)
    institution_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    email = serializers.EmailField(required=False, allow_null=True, default=None)
    first_name = serializers.CharField(required=False, allow_null=True, default=None)
    last_name = serializers.CharField(required=False, allow_null=True, default=None)

    class Meta:
        fields = ["learner_id", "institution_id", "email", "first_name", "last_name"]
