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
""" Learner Enrolment Requests Serializers """
from rest_framework import serializers


class EnrolmentSampleMetadataSerializer(serializers.Serializer):

    filename = serializers.CharField(required=False, allow_null=True, allow_blank=False, default=None)
    mimetype = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    context = serializers.JSONField(required=False, allow_null=True, default=None)

    class Meta:
        fields = ["filename", "mimetype", "context"]


class EnrolmentSampleSerializer(serializers.Serializer):
    """ Body serializer for enrolment sample request."""

    learner_id = serializers.UUIDField(required=True, allow_null=False)
    data = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    instruments = serializers.ListField(required=True, allow_null=False, allow_empty=False,
                                        child=serializers.IntegerField(allow_null=False))
    metadata = EnrolmentSampleMetadataSerializer(required=True, allow_null=False)

    class Meta:
        fields = ["learner_id", "data", "instruments", "metadata"]
