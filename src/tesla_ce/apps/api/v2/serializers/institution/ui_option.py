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
"""UI Option serialize module."""
from rest_framework import serializers

from tesla_ce.models import UIOption


class InstitutionUIOptionSerializer(serializers.ModelSerializer):
    """UI Option serialize model module."""

    institution_id = serializers.HiddenField(default=None, allow_null=True)
    is_global = serializers.SerializerMethodField()
    roles = serializers.ReadOnlyField()

    class Meta:
        model = UIOption
        fields = ['id', 'route', 'enabled', 'roles', 'user', 'institution_id', 'is_global']

    def get_is_global(self, instance):
        return instance.institution is None and instance.user is None

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

        # Check that this route is not already defined for the institution and same user
        qs = UIOption.objects.filter(route=attrs['route'],
                                     institution__id=self.context['view'].kwargs['parent_lookup_institution_id'])
        if attrs['user'] is not None:
            qs =  qs.filter(user=attrs['user'])
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        num_routes = qs.count()
        if num_routes > 0:
            raise serializers.ValidationError(detail="This route already exists")

        return super().validate(attrs)

    def validate_route(self, value):
        if value is None:
            raise serializers.ValidationError(detail="Route cannot be empty")

        if UIOption.objects.filter(route=value, institution=None, user=None).count() == 0:
            raise serializers.ValidationError(detail="Invalid Route")

        return value

    def validate_user(self, value):
        if value is not None and value.institution_id != int(
                self.context['view'].kwargs['parent_lookup_institution_id']
        ):
            raise serializers.ValidationError(detail="User must be from the institution")
        return value
