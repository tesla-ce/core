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
from rest_framework import serializers

from tesla_ce.models import VLE, Institution


class VLEInstitutionSerializer(serializers.ModelSerializer):
    """Institution serialize model module."""

    id = serializers.IntegerField(read_only=True)
    acronym = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = Institution
        fields = "__all__"


class VLESerializer(serializers.ModelSerializer):
    """VLE serialize model module."""
    type = serializers.CharField(source='get_type_display')
    institution = VLEInstitutionSerializer(many=False)

    class Meta:
        model = VLE
        exclude = ["lti", "created_at", "updated_at"]
