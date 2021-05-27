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
""" TeSLA Authentication views"""
import hvac
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from tesla_ce import models
from tesla_ce.apps.api.utils import decode_json
from tesla_ce.client import Client
from tesla_ce.lib.auth import JWTAuthentication
from tesla_ce.lib.auth import _get_token
from tesla_ce.lib.exception import TeslaAuthException
from . import serializers


class AuthSchema(AutoSchema):
    """ Schema definition for Authentication methods """
    def get_operation(self, path, method):
        default = super().get_operation(path, method)
        if path.endswith('user'):
            default['requestBody'] = {
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['email', 'password'],
                            'properties': {
                                'email': {
                                    'type': 'string',
                                },
                                'password': {
                                    'type': 'string',
                                },
                                'realm': {
                                    'type': 'string',
                                },
                            }
                        }
                    }
                }
            }
        elif path.endswith('approle'):
            default['requestBody'] = {
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['role_id', 'secret_id'],
                            'properties': {
                                'role_id': {
                                    'type': 'string',
                                },
                                'secret_id': {
                                    'type': 'string',
                                },
                            }
                        }
                    }
                }
            }
        elif path.endswith('token'):
            default['requestBody'] = {
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['token'],
                            'properties': {
                                'token': {
                                    'type': 'string',
                                }
                            }
                        }
                    }
                }
            }
        elif path.endswith('token/refresh'):
            default['requestBody'] = {
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'required': ['refresh_token'],
                            'properties': {
                                'refresh_token': {
                                    'type': 'string',
                                }
                            }
                        }
                    }
                }
            }

        return default


class AuthViewBase(APIView):
    """
        Base authentication view
    """
    # API TeSLA Client
    _client = Client(config=settings.TESLA_CONFIG)

    # Vault client to manage authentication requests
    _vault = hvac.Client(settings.TESLA_CONFIG.config.get('VAULT_URL'),
                         verify=settings.TESLA_CONFIG.config.get('VAULT_SSL_VERIFY'))

    permission_classes = ()
    authentication_classes = ()
    schema = AuthSchema()

    # Serializer for request body
    serializer_class = None
    alternative_serializer_class = None

    def get_authenticate_header(self, request):
        """
            Get the name of authentication token
            :param request: The HTTP request
            :return: Name of the token
        """
        return 'JWT'

    def authenticate(self, data):
        """
            Perform authentication using provided data

            :param data: Authentication data
            :return: Authenticated object or None if is not authenticated
        """
        return None

    @property
    def get_serializer(self):
        """
            Get the serializer for authentication object
            :return: Serializer class
            :rtype: class or None
        """
        return self.serializer_class

    @property
    def get_alternative_serializer(self):
        """
            Get alternative serializer for authentication class.
            :return: Serializer class
            :rtype: class or None
        """
        return self.alternative_serializer_class

    def get_entity_config(self, entity_id):
        """
            Get entity configuration data
            :param entity_id: Entity ID
            :return: Configuration data
        """
        entity_data = self._vault.secrets.kv.v2.read_secret_version(
            path='modules/{}/metadata'.format(entity_id),
            mount_point=self._client.config.config.get('VAULT_MOUNT_PATH_KV')
        )['data']['data']['data']
        entity_data['apps'] = self._vault.secrets.kv.v2.read_secret_version(
            path=entity_data['apps'],
            mount_point=self._client.config.config.get('VAULT_MOUNT_PATH_KV')
        )['data']['data']['data']
        entity_data['config'] = self._vault.secrets.kv.v2.read_secret_version(
            path=entity_data['config'],
            mount_point=self._client.config.config.get('VAULT_MOUNT_PATH_KV')
        )['data']['data']['data']
        entity_data['services'] = self._vault.secrets.kv.v2.read_secret_version(
            path=entity_data['services'],
            mount_point=self._client.config.config.get('VAULT_MOUNT_PATH_KV')
        )['data']['data']['data']

        config = {}
        for key, path in entity_data['config']:
            config[key] = self._vault.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self._client.config.config.get('VAULT_MOUNT_PATH_KV')
            )['data']['data']['value']
        entity_data['config'] = config

        return entity_data

    def post(self, request, *args, **kwargs):
        """
            Dispatcher for POST HTTP method
            :param request: The HTTP request
            :param args: Arguments provided to the request
            :param kwargs: Named arguments provided to the request
            :return: HTTP response
        """
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            if self.get_alternative_serializer is None:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_alternative_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        auth_data = self.authenticate(serializer.validated_data)
        if auth_data is None:
            return Response("Invalid credentials", status=status.HTTP_401_UNAUTHORIZED)

        # Add tokens
        auth_data = self._add_token(auth_data)

        return Response(auth_data, status=status.HTTP_200_OK)

    def get(self, request):
        """
            Dispatcher for GET HTTP method
            :param request: The HTTP request
            :return: HTTP response
        """
        return Response('Method not allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def _add_token(self, auth_data):
        """
            Add tokens for given authentication data

            :param auth_data: Authentication object
            :type auth_data: dict
            :return: Authenticated object with token information
            :rtype: dict
        """
        token = self._client.get_module_token(module_id='api', scope=['/api/*'],
                                              ttl=15, data={
                'type': auth_data['type'],
                'pk': auth_data['pk'],
            })

        refresh_token = self._client.get_module_token(module_id='api', scope=['/api/v2/auth/token/refresh'],
                                                      ttl=120,
                                                      data={
                                                          'ttl': 15,
                                                          'type': auth_data['type'],
                                                          'pk': auth_data['pk'],
                                                      }
                                                      )
        auth_data['token'] = {
            'access_token': token,
            'refresh_token': refresh_token
        }
        return auth_data


class UserPasswordView(AuthViewBase):
    """
        Authentication View for user/password credentials
    """
    serializer_class = serializers.AuthUserPasswordSerializer

    def authenticate(self, data):
        """
            Verify user credentials
            :param data: Provided credentials with email and password fields
            :return: Authenticated object or None if authentication fails
        """
        try:
            return self._client.verify_user(data['email'], data['password'])
        except TeslaAuthException:
            return None

    def _add_token(self, auth_data):
        return {
            'token': auth_data
        }


class AppRoleView(AuthViewBase):
    """
        Authentication View for role_id/secret_id credentials
    """
    serializer_class = serializers.AppRoleTokenSerializer

    def authenticate(self, data):
        """
            Verify module credentials
            :param data: Provided credentials with role_id and secret_id fields
            :return: Authenticated object or None if authentication fails
        """

        # Authenticate using approle credentials
        try:
            auth_resp = self._vault.auth.approle.login(
                data['role_id'],
                data['secret_id'],
                mount_point=self._client.config.config.get('VAULT_MOUNT_PATH_APPROLE')
            )
        except Exception:
            return None

        # Get the entity data
        entity_data = self.get_entity_config(auth_resp['auth']['metadata']['role_name'])

        # Get the module object
        if entity_data['module'].startswith('vle_'):
            entity_data['type'] = 'vle'
            entity_data['pk'] = entity_data['vle_id']
            # Get VLE information
            try:
                vle = models.VLE.objects.get(pk=entity_data['vle_id'])
            except models.VLE.DoesNotExist:
                return None
            entity_data['vle'] = serializers.VLESerializer(instance=vle).data

        elif entity_data['module'].startswith('provider_'):
            entity_data['type'] = 'provider'
            entity_data['pk'] = entity_data['provider_id']
            # Get Provider information
            try:
                provider = models.Provider.objects.get(pk=entity_data['provider_id'])
            except models.Provider.DoesNotExist:
                return None
            entity_data['provider'] = serializers.ProviderSerializer(instance=provider).data
        else:
            return None

        return entity_data


class TokenObtainPairView(AuthViewBase):
    """
        Token based authentication view
    """
    serializer_class = serializers.AuthTokenSerializer

    def authenticate(self, data):
        """
            Verify token
            :param data: Provided credentials with id and token fields
            :return: Authenticated object or None if authentication fails
        """
        with transaction.atomic():
            try:
                launcher = models.Launcher.objects.get(id=data['id'],
                                                       token=data['token'])
            except models.Launcher.DoesNotExist:
                return None
        return launcher.token_pair

    def _add_token(self, auth_data):
        return decode_json(auth_data)


class TokenRefreshView(AuthViewBase):
    """
        Refresh token view
    """
    serializer_class = serializers.AuthTokenRefreshSerializer
    alternative_serializer_class = serializers.AlternativeAuthTokenRefreshSerializer

    def authenticate(self, data):
        """
            Verify credentials
            :param data: Provided credentials
            :return: Authenticated object or None if authentication fails
        """
        return data

    def _add_token(self, auth_data):
        token = auth_data['token']
        if 'access_token' in token and 'refresh_token' in token:
            access_token = token['access_token']
            refresh_token = token['refresh_token']
        else:
            access_token = token
            refresh_token = _get_token(self.request)
        try:
            access_token = self._client.refresh_token(access_token, refresh_token)
        except TeslaAuthException as exc:
            raise PermissionDenied(exc) from exc
        return {
            "token": {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        }


class LogOut(APIView):
    """
        Perform system log out
    """
    def delete(self, request):
        """
            Dispatcher for delete HTTP method
            :param request: The HTTP request
            :return: A HTTP response
        """
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class UserDataView(APIView):
    """
        Get user data
    """
    permission_classes = ()
    authentication_classes = ()
    _authenticator = JWTAuthentication()

    def get(self, request):
        """
            Dispatcher for GET HTTP method

            :param request: The HTTP request
            :return: A HTTP response
        """
        try:
            user, _ = self._authenticator.authenticate(request)
        except TeslaAuthException:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if user.id is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.UserDataSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


user_view = UserPasswordView.as_view()
app_view = AppRoleView.as_view()
token_view = TokenObtainPairView.as_view()
token_refresh_view = TokenRefreshView.as_view()
user_data_view = UserDataView.as_view()
logout_view = LogOut.as_view()
