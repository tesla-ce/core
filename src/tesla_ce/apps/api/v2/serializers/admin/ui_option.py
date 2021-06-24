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
from tesla_ce.models.user import get_roles


class UIOptionSerializer(serializers.ModelSerializer):
    """UI Option serialize model module."""

    id = serializers.ReadOnlyField()

    class Meta:
        model = UIOption
        fields = ['id', 'route', 'enabled', 'roles']

    def validate_route(self, value):
        """
            Check that provided route is valid
            :param value: New UI Option route
            :return: Route
        """
        if value is None:
            raise serializers.ValidationError(detail="Route cannot be empty")
        qs = UIOption.objects.filter(route=value)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)
        num_routes = qs.count()
        if num_routes > 0:
            raise serializers.ValidationError(detail="This route already exists")
        return value

    def validate_roles(self, value):
        """
            Check that provided roles are valid
            :param value: New UI Option route
            :return: Route
        """
        if value is None or len(value.strip()) == 0:
            return None

        valid_roles = get_roles()
        list_roles = value.split(',')
        roles = []
        for role in list_roles:
            if role.upper() not in valid_roles:
                raise serializers.ValidationError(detail="Role {} is not valid".format(role))
            roles.append(role.upper())
        return ','.join(roles)
