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
""" TeSLA Authentication serializers """
import json

from rest_framework import serializers

from tesla_ce.models import Institution
from tesla_ce.models import Provider
from tesla_ce.models import VLE
from tesla_ce.models.user import get_institution_roles
from tesla_ce.models.ui_option import get_user_ui_routes


class JSONField(serializers.JSONField):
    """ JSON field object used in serializers """

    def to_representation(self, value):
        """
            Parse input data
            :param value: The object value
            :return: A JSON representation
        """
        if isinstance(value, str) and len(value) == 0:
            value = None
        if value is not None and isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                pass
        return super().to_representation(value)


class VLESerializer(serializers.ModelSerializer):
    """VLE serialize model module."""

    lti = JSONField()

    class Meta:
        model = VLE
        fields = "__all__"


class ProviderSerializer(serializers.ModelSerializer):
    """Provider serialize model module."""

    options = JSONField(allow_null=True)
    options_schema = JSONField(allow_null=True)

    class Meta:
        model = Provider
        fields = "__all__"


class AuthUserPasswordSerializer(serializers.Serializer):
    """ Body serializer for user/password authentication."""

    email = serializers.EmailField(required=True, allow_null=False)
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    realm = serializers.CharField(allow_null=False, allow_blank=False, default="api")

    class Meta:
        fields = ["email", "password", "realm"]

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class AppRoleTokenSerializer(serializers.Serializer):
    """ Body serializer for approle based authentication."""

    role_id = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    secret_id = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        fields = ["role_id", 'secret_id']

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class AuthTokenSerializer(serializers.Serializer):
    """ Body serializer for token based authentication."""

    token = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    id = serializers.IntegerField(required=True, allow_null=False)

    class Meta:
        fields = ["token", "id"]

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class AuthTokenRefreshSerializer(serializers.Serializer):
    """ Body serializer for token refresh."""

    token = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        fields = ["token"]

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class AuthTokenPairSerializer(serializers.Serializer):
    """ Serializer for token pair."""

    access_token = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    refresh_token = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        fields = ["access_token", "refresh_token"]

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class AlternativeAuthTokenRefreshSerializer(serializers.Serializer):
    """ Body serializer for token refresh for Angular."""

    token = AuthTokenPairSerializer(required=True, allow_null=False)

    class Meta:
        fields = ["token"]

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class UserDataInstitutionSerializer(serializers.Serializer):
    """ Serializer for user data."""
    id = serializers.IntegerField(required=True, allow_null=False)
    acronym = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        fields = ["id", "acronym", "name"]

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')


class UserDataSerializer(serializers.Serializer):
    """ Serializer for user data."""
    id = serializers.IntegerField(required=True, allow_null=False)
    first_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    username = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    email = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    is_admin = serializers.BooleanField(source='is_staff', required=True, allow_null=False)
    full_name = serializers.SerializerMethodField()
    uid = serializers.CharField(required=False, allow_null=True, allow_blank=False, default=None)
    locale = serializers.CharField(required=False, allow_null=True, allow_blank=False, default=None)
    institution = serializers.SerializerMethodField(read_only=True)
    institutions = serializers.SerializerMethodField(read_only=True)
    roles = serializers.SerializerMethodField(read_only=True)
    routes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ["first_name", "last_name", "username", "email", "is_admin", "full_name", "uid", "locale",
                  "institution", "roles"]

    @staticmethod
    def get_full_name(instance):
        """
            Get full name of the user
            :param instance: User instance
            :return: Full name
        """
        return instance.first_name + ' ' + instance.last_name

    @staticmethod
    def get_institution(instance):
        """
            Get institution information for user
            :param instance: User instance
            :return: Institution information
        """

        if hasattr(instance, "institutionuser"):
            roles = get_institution_roles(instance)
            try:
                learner_id = str(instance.institutionuser.learner.learner_id)
            except Exception:
                learner_id = None

            return {
                "id": instance.institutionuser.institution.id,
                "acronym": instance.institutionuser.institution.acronym,
                "uid": instance.institutionuser.uid,
                "roles": roles,
                "locale": instance.institutionuser.locale,
                "learner_id": learner_id
            }

        return None

    def get_institutions(self, instance):
        """
            Get list of institutions for user
            :param instance: User instance
            :return: Institutions list
        """
        institutions = []
        if 'GLOBAL_ADMIN' in self.get_roles(instance):
            for institution in Institution.objects.all().order_by('acronym'):
                institutions.append({
                    "id": institution.id,
                    "acronym": institution.acronym,
                    "uid": None,
                    "roles": ['GLOBAL_ADMIN'],
                    "locale": None,
                })
        else:
            default_institution = self.get_institution(instance)
            if default_institution is not None:
                institutions.append(default_institution)

        return institutions

    def get_roles(self, instance):
        """
            Get the list of roles for a user
            :param instance: User instance
            :return: List of roles
        """
        roles = []
        inst = self.get_institution(instance)
        if inst is not None:
            roles = inst['roles']
        if instance.is_staff:
            roles.append('GLOBAL_ADMIN')

        return roles

    @staticmethod
    def get_routes(instance):
        """
            Get the list of allowed routes for the user
            :param instance: User object
            :return: List of allowed routes
        """
        return get_user_ui_routes(instance)

    def update(self, instance, validated_data):
        """
            Update existing instance
            :param instance: The current instance
            :param validated_data: The new data
            :return: Updated instance
        """
        raise NotImplementedError('Operation not permitted')

    def create(self, validated_data):
        """
            Create a new instance
            :param validated_data: The data for the new instance
            :return: New instance
        """
        raise NotImplementedError('Operation not permitted')
