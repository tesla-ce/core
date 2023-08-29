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
""" Alert serializer module """
import json

from rest_framework import serializers
from tesla_ce.models import Alert, Message


class MessageSerializer(serializers.ModelSerializer):
    """Message serialize model module."""
    class Meta:
        model = Message
        fields = "__all__"


class AlertSerializer(serializers.ModelSerializer):
    """Alert serialize model module."""
    data = serializers.SerializerMethodField()
    message = MessageSerializer(read_only=True, many=False, source='message_code', required=False)

    class Meta:
        model = Alert
        fields = "__all__"

    @staticmethod
    def get_data(obj):
        """ Get data """
        content = {}

        with obj.data.open() as f:
            try:
                content_json = f.read().decode('utf-8')
                content = json.loads(content_json)
            except Exception:
                pass

        return content
