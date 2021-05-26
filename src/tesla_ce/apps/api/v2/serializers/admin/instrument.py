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
"""Instrument api serialize module."""
from rest_framework import serializers

from tesla_ce.apps.api.utils import JSONField
from tesla_ce.models import Instrument


class InstrumentSerializer(serializers.ModelSerializer):
    """Instrument serialize model module."""
    options_schema = JSONField(allow_null=True, required=False, default=None
                               )
    class Meta:
        model = Instrument
        fields = "__all__"
