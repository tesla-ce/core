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
"""VLE api serialize module."""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tesla_ce.apps.api.utils import JSONField

from tesla_ce.models import AssessmentSession
from tesla_ce.models import AssessmentSessionData


class VLENewAssessmentSessionBodySerializer(serializers.Serializer):
    vle_activity_type = serializers.CharField(required=False, allow_blank=False, allow_null=False)
    vle_activity_id = serializers.CharField(required=False, allow_blank=False, allow_null=False)
    vle_learner_uid = serializers.CharField(required=False, allow_blank=False, allow_null=False)
    locale = serializers.CharField(required=False, allow_null=True, default=None)
    max_ttl = serializers.IntegerField(required=False, allow_null=False, default=120)
    session_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    redirect_reject_url = serializers.URLField(required=False, allow_null=True, default=None)
    reject_message = serializers.CharField(required=False, allow_null=True, default=None)
    options = JSONField(required=False, allow_null=True, default=True)
    close = serializers.BooleanField(required=False, allow_null=True, default=False)

    class Meta:
        fields = ["vle_activity_type", "vle_activity_id", "vle_learner_uid", "locale", "max_ttl",
                  "session_id", "redirect_reject_url", "reject_message", "options", "close"]

    def validate(self, attrs):
        """
            Vaidate data
            :param attrs: Provided data
            :return: validated data
        """
        if 'session_id' not in attrs or attrs['session_id'] is None:
            if 'vle_activity_type' not in attrs or attrs['vle_activity_type'] is None:
                raise ValidationError('Missing vle_activity_type value')
            if 'vle_activity_id' not in attrs or attrs['vle_activity_id'] is None:
                raise ValidationError('Missing vle_activity_id value')
            if 'vle_learner_uid' not in attrs or attrs['vle_learner_uid'] is None:
                raise ValidationError('Missing vle_learner_uid value')
        return super().validate(attrs)


class VLENewAssessmentSessionDataSerializer(serializers.ModelSerializer):
    """New assessment session data serialize module."""

    class Meta:
        model = AssessmentSessionData
        fields = "__all__"


class VLENewAssessmentSessionSerializer(serializers.ModelSerializer):
    """New assessment session serialize module."""
    data = VLENewAssessmentSessionDataSerializer(source='assessmentsessiondata', many=False, read_only=True)

    class Meta:
        model = AssessmentSession
        fields = "__all__"
