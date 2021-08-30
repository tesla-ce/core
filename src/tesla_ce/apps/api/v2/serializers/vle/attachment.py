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
""" Activity Attachment serialize module """
from rest_framework import serializers
from tesla_ce.apps.lapi.serializers import VerificationSampleSerializer


class VLECourseActivityAttachmentSerializer(VerificationSampleSerializer):
    """Activity attachment serialize model module."""

    learner_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    course_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    activity_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    close_session = serializers.BooleanField(required=False, allow_null=True, default=True, write_only=True)
    close_at = serializers.DateTimeField(required=False, allow_null=False, default=None)

    class Meta:
        fields = ["learner_id", "course_id", "activity_id", "session_id", "data", "instruments", "metadata",
                  "close_at", "close_session"]
