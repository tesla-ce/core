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
from django.conf import settings
from rest_framework import serializers


class VLELauncherBodySerializer(serializers.Serializer):
    vle_user_uid = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    target = serializers.ChoiceField(required=False, allow_null=False, default="DASHBOARD", choices=("DASHBOARD", "LAPI",))
    target_url = serializers.CharField(required=False, allow_null=True, default=None)
    ttl = serializers.IntegerField(required=False, allow_null=False, default=120)
    session_id = serializers.IntegerField(required=False, allow_null=True, default=None)

    class Meta:
        fields = ["vle_user_uid", "target", "target_url", "ttl", "session_id"]


class VLELauncherDataSerializer(serializers.Serializer):
    """New launcher data."""

    token = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    id = serializers.IntegerField(required=True, allow_null=False)
    url = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "token", "url"]

    def get_url(self, object):
        return "{}/ui/auth/launcher?id={}&token={}".format(settings.DASHBOARD_URL, object['id'], object['token'])
