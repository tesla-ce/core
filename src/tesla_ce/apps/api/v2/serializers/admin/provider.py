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
"""Provider api serialize module."""
import jsonschema
from rest_framework import serializers

from tesla_ce.apps.api.utils import JSONField
from tesla_ce.apps.api.utils import JSONFormField
from tesla_ce.apps.api.utils import decode_json
from tesla_ce.models import Provider
from .instrument import InstrumentSerializer


class ProviderSerializer(serializers.ModelSerializer):
    """Provider serialize model module."""
    instrument = InstrumentSerializer(read_only=True)
    name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    url = serializers.URLField(read_only=True)
    version = serializers.CharField(read_only=True)
    acronym = serializers.CharField(read_only=True)
    allow_validation = serializers.BooleanField(read_only=True)
    inverted_polarity = serializers.BooleanField(read_only=True)
    image = serializers.CharField(read_only=True)
    has_service = serializers.BooleanField(read_only=True)
    service_port = serializers.IntegerField(read_only=True)
    options_schema = JSONField(read_only=True)
    #options = JSONField(allow_null=True, default=None)
    options = JSONFormField(allow_null=True, default=None, schema='options_schema')

    class Meta:
        model = Provider
        fields = "__all__"

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['instrument_id'] = self.context['view'].kwargs['parent_lookup_instrument_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)

    def validate_options(self, value):
        if value is not None:
            schema = decode_json(self.instance.options_schema)
            try:
                jsonschema.validate(instance=value, schema=schema)
            except jsonschema.exceptions.ValidationError as error:
                raise serializers.ValidationError(detail=error.message)
            else:
                return value
        return None

