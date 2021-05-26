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
""" TeSLA Identity Provider Serializers """
from rest_framework import serializers


class LearnerIdSerializer(serializers.Serializer):
    """ Body serializer for a single mail."""

    mail = serializers.EmailField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        fields = "mail"


class MultipleLearnerIdSerializer(serializers.Serializer):
    """ Body serializer for a single mail."""

    mails = serializers.ListField(required=True, child=serializers.EmailField(), allow_null=False)

    class Meta:
        fields = "mails"


class LearnerSerializer(serializers.Serializer):
    """ Learner serialization """

    tesla_id = serializers.UUIDField(source='learner_id', read_only=True)
    mail = serializers.EmailField(source='email', read_only=True)

    class Meta:
        fields = ["teala_id", "mail"]
