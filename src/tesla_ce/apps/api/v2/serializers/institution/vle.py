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
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework import validators

from tesla_ce import get_default_client
from tesla_ce.apps.api.utils import JSONField
from tesla_ce.lib.exception import TeslaVaultException
from tesla_ce.models import VLE
from tesla_ce.models.vle import VLE_TYPE


class InstitutionVLESerializer(serializers.ModelSerializer):
    """VLE serialize model module."""
    _credentials = None

    type = serializers.ChoiceField(choices=VLE_TYPE)
    lti = JSONField(read_only=True)
    name = serializers.CharField(validators=[
                                    validators.UniqueValidator(queryset=VLE.objects.all())
                                 ])

    credentials = serializers.SerializerMethodField(default=None)

    class Meta:
        model = VLE
        exclude = ["created_at", "updated_at", "institution"]

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

    def create(self, validated_data):
        vle = super().create(validated_data)

        try:
            vle_info = get_default_client().register_vle(vle.get_type_display(), vle.name, vle.url,
                                                         vle.institution.acronym, vle.client_id, True)
        except TeslaVaultException:
            vle.delete()
            raise exceptions.PermissionDenied('Cannot register VLEs')

        self._credentials = vle_info

        return vle

    def get_credentials(self, object):
        return self._credentials
