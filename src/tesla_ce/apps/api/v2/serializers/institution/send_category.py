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
"""SENDCategory api serialize module."""
import json

from rest_framework import serializers

from tesla_ce.models import Instrument
from tesla_ce.models import SENDCategory
from .institution import InstitutionSerializer


def get_instruments():
    return [(inst.id, inst.name) for inst in Instrument.objects.all()]


class InstitutionSENDCategoryDataSerializer(serializers.Serializer):
    """SENDCategory serialize data module."""

    enabled_options = serializers.MultipleChoiceField(choices=['big_fonts', 'high_contrast', 'text_to_speech'],
                                                      required=False)
    disabled_instruments = serializers.MultipleChoiceField(choices=get_instruments(),
                                                           required=False)

    def to_internal_value(self, data):
        data_object = super().to_internal_value(data)
        data_object['enabled_options'] = list(data_object['enabled_options'])
        data_object['disabled_instruments'] = list(data_object['disabled_instruments'])

        return json.dumps(data_object)

    def to_representation(self, instance):
        if isinstance(instance, str):
            return json.loads(instance)
        return instance


class InstitutionSENDCategorySerializer(serializers.ModelSerializer):
    """SENDCategory serialize model module."""

    institution = InstitutionSerializer(read_only=True)
    data = InstitutionSENDCategoryDataSerializer(default={})
    institution_id = serializers.HiddenField(default=None, allow_null=True)

    class Meta:
        model = SENDCategory
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
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_institution_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
