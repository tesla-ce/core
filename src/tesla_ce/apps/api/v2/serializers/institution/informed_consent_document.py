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
"""InformedConsentDocument api serialize module."""
from rest_framework import serializers

from tesla_ce.models import InformedConsentDocument
from .informed_consent import InstitutionInformedConsentSerializer


class InstitutionInformedConsentDocumentSerializer(serializers.ModelSerializer):
    """InformedConsentDocument serialize model module."""

    consent = InstitutionInformedConsentSerializer(read_only=True)

    class Meta:
        model = InformedConsentDocument
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
        #attrs['institution_id'] = self.context['view'].kwargs['parent_lookup_institution_id']
        attrs['consent_id'] = self.context['view'].kwargs['parent_lookup_informed_consent_id']

        # Apply validators
        for validator in self.get_validators():
            validator(attrs, self)
        return super().validate(attrs)
