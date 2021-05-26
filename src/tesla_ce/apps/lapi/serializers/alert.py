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
""" Learner Alert messages Serializers """
from rest_framework import serializers


class AlertMessageSerializer(serializers.Serializer):
    """ Body serializer for alert messages."""

    level = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    learner_id = serializers.UUIDField(required=True, allow_null=False)
    course_id = serializers.IntegerField(required=True, allow_null=False)
    activity_id = serializers.IntegerField(required=True, allow_null=False)
    session_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    instruments = serializers.ListField(required=False, allow_null=True, allow_empty=True, default=None,
                                        child=serializers.IntegerField(allow_null=False))
    data = serializers.JSONField(required=True, allow_null=False)
    raised_at = serializers.DateTimeField(required=True, allow_null=False)

    class Meta:
        fields = ["level", "learner_id", "course_id", "activity_id", "session_id", "data", "instruments", "raised_at"]
