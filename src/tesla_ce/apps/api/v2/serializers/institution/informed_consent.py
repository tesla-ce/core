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
"""InformedConsent api serialize module."""
from rest_framework import serializers

from tesla_ce.models import InformedConsent
from .institution import InstitutionSerializer


class InstitutionInformedConsentVersionSerializer(serializers.ModelSerializer):
    """InformedConsent serialize model module."""
    class Meta:
        model = InformedConsent
        fields = "version"


class InstitutionInformedConsentSerializer(serializers.ModelSerializer):
    """InformedConsent serialize model module."""

    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.HiddenField(default=None, allow_null=True)

    class Meta:
        model = InformedConsent
        fields = "__all__"
        validators = [serializers.UniqueTogetherValidator(
            queryset=InformedConsent.objects.all(),
            fields=['institution_id', 'version']
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
        attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_institution_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)

    @classmethod
    def validate_version(self, value):
        """
            Validate the version format
            :param value: Provided version value
            :type value: str
            :return: Validated version
            :rtype: str
        """
        # Check version format
        try:
            version = [int(i) for i in value.split('.')]
            if len(version) != 3:
                raise ValueError()
        except ValueError:
            raise serializers.ValidationError('Invalid version. Expected X.Y.Z with X, Y and Z integer values')

        return '.'.join([str(i) for i in version])
