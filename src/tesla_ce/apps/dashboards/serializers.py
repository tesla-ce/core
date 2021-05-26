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
""" Dashboards serializers module"""
from rest_framework import serializers

from tesla_ce import models


class LoginSerializer(serializers.Serializer):
    """
        Serializer for login data
    """
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)


class TokenSerializer(serializers.Serializer):
    """
        Serializer for token data
    """
    token = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)



class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AssessmentSession
        fields = "__all__"


class AlertSerializer(serializers.ModelSerializer):

    data = serializers.JSONField(allow_null=True)

    class Meta:
        model = models.Alert
        fields = ["id", "level", "get_level_display", "raised_at", "data"]


class RequestResultSerializer(serializers.ModelSerializer):

    instrument = serializers.CharField(source="instrument.acronym")

    class Meta:
        model = models.RequestResult
        fields = ["id", "status", "get_status_display", "result", "code", "get_code_display", "instrument"]


class RequestProviderResultSerializer(serializers.ModelSerializer):

    provider = serializers.CharField(source="provider.acronym")
    instrument = serializers.CharField(source="provider.instrument.acronym")

    class Meta:
        model = models.RequestProviderResult
        fields = ["id", "status", "get_status_display", "result", "code", "get_code_display", "provider", "instrument"]


class RequestSerializer(serializers.ModelSerializer):

    results = RequestResultSerializer(source="requestresult_set", many=True)
    providers = RequestProviderResultSerializer(source="requestproviderresult_set", many=True)

    class Meta:
        model = models.Request
        fields = ["id", "status", "created_at", "updated_at", "get_status_display", "results", "providers"]
