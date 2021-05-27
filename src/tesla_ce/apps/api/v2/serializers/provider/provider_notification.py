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
""" Provider notification serializers module """
from rest_framework import serializers

from tesla_ce.apps.api.utils import JSONField
from tesla_ce.models import ProviderNotification


class ProviderNotificationSerializer(serializers.ModelSerializer):
    """Provider notification serialize class."""
    info = JSONField(allow_null=True, default=None)
    provider_id = serializers.HiddenField(default=None)
    provider = serializers.IntegerField(read_only=True, source="provider_id")

    class Meta:
        model = ProviderNotification
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
        attrs['provider_id'] = self.context['view'].kwargs['parent_lookup_provider_id']

        try:
            self.instance = ProviderNotification.objects.get(provider_id=attrs['provider_id'],
                                                             key=attrs['key'])
        except ProviderNotification.DoesNotExist:
            pass

        return super().validate(attrs)

    def update(self, instance, validated_data):

        if instance.info is not None and validated_data.get('info') is not None:
            new_info = JSONField().to_representation(instance.info)
            new_info.update(validated_data['info'])
            validated_data['info'] = new_info

        return super().update(instance, validated_data)
