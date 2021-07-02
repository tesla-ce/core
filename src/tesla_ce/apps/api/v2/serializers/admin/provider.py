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

from rest_framework import exceptions
from rest_framework import serializers

from tesla_ce import get_default_client
from tesla_ce.apps.api.utils import decode_json
from tesla_ce.apps.api.utils import JSONField
from tesla_ce.apps.api.utils import JSONFormField
from tesla_ce.lib.exception import TeslaVaultException
from tesla_ce.models import Instrument
from tesla_ce.models import Provider
from .instrument import InstrumentSerializer


class ProviderSerializer(serializers.ModelSerializer):
    """Provider serialize model module."""
    _credentials = None

    id = serializers.ReadOnlyField()
    instrument = InstrumentSerializer(read_only=True)
    instrument_id = serializers.HiddenField(default=None, allow_null=True)
    options_schema = JSONField(allow_null=True, default=None)
    options = JSONFormField(allow_null=True, default=None, schema='options_schema')
    enabled = serializers.BooleanField(allow_null=True, default=False)
    validation_active = serializers.BooleanField(allow_null=True, default=False)

    credentials = serializers.SerializerMethodField(default=None, read_only=True)

    class Meta:
        model = Provider
        fields = ['id', 'instrument_id', 'instrument', 'name', 'queue', 'description', 'url', 'version', 'acronym',
                  'allow_validation', 'inverted_polarity', 'image', 'has_service', 'service_port', 'options_schema',
                  'options', 'credentials', 'enabled', 'validation_active']

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
        attrs['instrument'] = Instrument.objects.get(id=attrs['instrument_id'])

        # Check options and schema
        if 'options' in attrs or 'options_schema' in attrs:
            options_schema = attrs.get('options_schema')
            if options_schema is None and 'options_schema' not in attrs and self.instance is not None:
                options_schema = decode_json(self.instance.options_schema)
            options = attrs.get('options')
            if options is None and 'options' not in attrs and self.instance is not None:
                options = decode_json(self.instance.options)
            if options_schema is None and options is not None:
                raise serializers.ValidationError(detail="Options are not compatible with the NULL provided schema")
            if options is not None:
                try:
                    jsonschema.validate(instance=options, schema=options_schema)
                except jsonschema.exceptions.ValidationError as val_err:
                    raise serializers.ValidationError(detail=val_err) from val_err

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)

    def create(self, validated_data):
        provider = super().create(validated_data)

        try:
            provider_info = get_default_client().register_provider(validated_data, force_update=True)
        except TeslaVaultException:
            provider.delete()
            raise exceptions.PermissionDenied('Cannot register Provider')

        self._credentials = provider_info

        return provider

    def get_credentials(self, object):
        return self._credentials
