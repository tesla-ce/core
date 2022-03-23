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
""" Activity instruments serializer module """
from rest_framework import serializers

from tesla_ce.apps.api.utils import JSONFormField
from tesla_ce.models import ActivityInstrument
from tesla_ce.models import Instrument


class InstitutionCourseActivityInstrumentInfoSerializer(serializers.ModelSerializer):
    """Instruments serialize model module."""

    class Meta:
        model = Instrument
        fields = "__all__"


class InstitutionCourseActivityInstrumentSerializer(serializers.ModelSerializer):
    """Activity instruments serialize model module."""

    activity_id = serializers.HiddenField(default=None, allow_null=True)
    options = JSONFormField(allow_null=True, schema='instrument.options_schema', default=None)
    instrument = InstitutionCourseActivityInstrumentInfoSerializer(many=False, read_only=True)
    instrument_id = serializers.IntegerField(allow_null=False, write_only=True)

    class Meta:
        model = ActivityInstrument
        exclude = ["activity"]
        validators = [serializers.UniqueTogetherValidator(
            queryset=ActivityInstrument.objects.all(),
            fields=['activity_id', 'instrument_id']
        ), ]

    def validate(self, attrs):
        """
            Validate the given attributes
            :param attrs: Attributes parsed from request
            :type attrs: dict
            :return: Validated attributes
            :rtype: dict
        """
        # Add predefined fields
        attrs['activity_id'] = self.context['view'].kwargs['parent_lookup_activity_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
