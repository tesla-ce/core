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
""" TeSLA API utility module """
import json

from rest_framework import serializers
from rest_framework.fields import empty


def decode_json(value):
    """
        Decode a JSON from String
        :param value: String JSON object
        :type value: str
        :return: JSON object
        :rtype: dict
    """
    if value is not None and isinstance(value, str):
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError:
            json_value = value.replace('\'', '"')
            json_value = json_value.replace('False', 'false').replace('True', 'true')
            json_value = json_value.replace('None', 'null')
            return json.loads(json_value)
    return value


class JSONField(serializers.JSONField):
    """ Deal with JSON fields """

    def to_representation(self, value):
        """
            Creates a representation for a JSON field
            :param value: Field value
            :return: Representation or the value
        """
        if isinstance(value, str) and len(value) == 0:
            value = None
        if value is not None and isinstance(value, str):
            return decode_json(value)
        return json.loads(json.dumps(value))

    def to_internal_value(self, data):
        return super().to_internal_value(data)


class BodySerializer(serializers.Serializer):
    """ Utility base serializer for custom request body """

    def update(self, instance, validated_data):
        """
            Method called when the represented object is modified.
            :param instance: Current instance
            :param validated_data: Validated data
            :return: Updated instance
        """
        return instance

    def create(self, validated_data):
        """
            Method called when a new object is created.
            :param validated_data: Validated data
            :return: Created instance
        """
        return None


class JSONFormField(JSONField):
    schema = None

    def __init__(self, *args, **kwargs):
        self.schema = self.schema = kwargs.pop('schema', None)

        assert self.schema is not None, "Schema parameter is required"

        super().__init__(*args, **kwargs)

    def run_validation(self, data=empty):
        valid_data = super().run_validation(data)
        return valid_data
