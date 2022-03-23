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
# TeSLA CE Authentication Middleware
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from tesla_ce import models
from tesla_ce.client import TeslaAuthException
from tesla_ce.client import get_default_client
from tesla_ce.models.user import AuthenticatedModule
from tesla_ce.models.user import AuthenticatedUser
from tesla_ce.models.user import UnauthenticatedUser


def _get_token(request):
    """
        Extract the authentication token from a request

        :param request: The request
        :type request: django.http.request
        :return: The token or None if it is not provided
        :rtype: str
    """
    # Get the Authentication header
    auth_header = request.headers.get('authorization')

    # Check if it contains a TeSLA JWT token
    if auth_header.startswith(settings.TESLA_JWT_TOKEN):
        token = auth_header.split()
        if len(token) == 2:
            token = token[1]
            return token
    return None


def _is_allowed_url(request, scopes, filters=None):
    """
        Check if current request is allowed

        :param request: The request to be checked
        :type request: django.http.request
        :param scopes: List o allowed scopes
        :type scopes: list
        :param filters: List of filtered scopes
        :type filters: list
        :return: True if it is allowed or False otherwise
        :rtype: bool
    """
    return True


def is_authenticated_request(request):
    """
        Check if a request is authenticated or not

        :param request: A request
        :type request: django.
        :return: None if it is not authenticated or the payload if it is valid
        :rtype: dict
    """
    # Get the token
    token = _get_token(request)

    if token is not None:
        payload = get_default_client().validate_token(token)
        if _is_allowed_url(request, payload.get('scope'), payload.get('filters')):
            return payload

    return None


def _authenticate(request, token):
    # Validate the token
    user = UnauthenticatedUser()
    try:
        validation = get_default_client().validate_token(token=token)
        if validation['valid']:
            user = UnauthenticatedUser()
    except TeslaAuthException:
        pass

    # Set the user to the request
    request.user = user


class JWTAuthentication(BaseAuthentication):
    """
        Authentication class for DJango Rest Framework
    """
    # Client used to verify tokens
    _client = get_default_client()

    def authenticate(self, request):
        """
            Authenticate the request and return a two-tuple of (user, token).

            :return: A two-tuple of (user, token).
            :rtype: tuple
        """
        # Get the Authentication header
        auth = get_authorization_header(request).split()

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)

        if len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)

        if len(auth) == 0:
            return UnauthenticatedUser(), None

        try:
            token = auth[1].decode()
        except UnicodeError as eue:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise AuthenticationFailed(msg) from eue

        return self.authenticate_credentials(token)

    def _get_module_model(self, payload):
        """
            Get the corresponding module model from payload information
            :param payload: Extracted payload
            :return: Module instance
        """
        user = AuthenticatedModule()
        if payload['type'] == 'provider':
            try:
                user.module = models.Provider.objects.get(pk=payload['pk'])
            except models.Provider.DoesNotExist as dne:
                raise AuthenticationFailed(_('Invalid provider.')) from dne
        elif payload['type'] == 'vle':
            try:
                user.module = models.VLE.objects.get(pk=payload['pk'])
            except models.VLE.DoesNotExist as dne:
                raise AuthenticationFailed(_('Invalid VLE.')) from dne
        else:
            raise AuthenticationFailed(_('Invalid module type.'))

        user.id = None
        user.type = payload['type']
        user.pk = payload['pk']
        user.username = payload['sub']

        return user

    def _get_user_model(self, payload):
        """
            Get the corresponding user model from payload information
            :param payload: Extracted payload
            :return: User instance
        """
        if payload['group'] == 'learners':
            try:
                user = models.Learner.objects.get(learner_id=payload['sub'])
            except models.Learner.DoesNotExist as dne:
                raise AuthenticationFailed(_('Invalid learner.')) from dne
        elif payload['group'] == 'users':
            if payload['type'] == 'admin':
                try:
                    user = models.User.objects.get(pk=payload['pk'])
                except models.User.DoesNotExist as dne:
                    raise AuthenticationFailed(_('Invalid user.')) from dne
            else:
                try:
                    user = models.InstitutionUser.objects.get(uid=payload['sub'])
                except models.InstitutionUser.DoesNotExist:
                    try:
                        user = models.InstitutionUser.objects.get(id=payload['pk'])
                    except models.InstitutionUser.DoesNotExist as dne:
                        raise AuthenticationFailed(_('Invalid user.')) from dne
        elif payload['group'].startswith('module_'):
            user = self._get_module_model(payload)
        else:
            raise AuthenticationFailed(_('Invalid payload group.'))
        return user

    def authenticate_credentials(self, token):
        """
            Check provided token and perform authentication

            :param token: The JWT token provided
            :type token: str
            :return: A two-tuple of (user, token).
            :rtype: tuple
        """
        user = UnauthenticatedUser()
        try:
            payload = self._client.validate_token(token=token)
            if len(settings.DATABASES) > 0 and settings.DATABASES['default']['ENGINE'] != 'django.db.backends.dummy':
                user = self._get_user_model(payload)
            else:
                user = AuthenticatedUser()
                user.type = payload['type']
                user.allowed_scopes = payload['scope']
                user.sub = payload['sub']
                user.pk = payload['pk']
                user.filters = payload['filters']

        except TeslaAuthException as exc:
            raise AuthenticationFailed(_('Invalid token: {}'.format(exc))) from exc

        if not user.is_active:
            raise AuthenticationFailed(_('User inactive or deleted.'))

        return user, token

    def authenticate_header(self, request):
        """
            Return a string to be used as the value of the `WWW-Authenticate`
            header in a `401 Unauthenticated` response, or `None` if the
            authentication scheme should return `403 Permission Denied` responses.
        """
        return "JWT"


def tesla_token_auth_middleware(get_response):
    """
        TeSLA Authentication Middleware.
        :param get_response:
        :return:
    """

    def middleware(request):

        # Extract the token
        token = _get_token(request)

        # Authenticate the request
        if token is not None:
            # Get user from token
            _authenticate(request, token)
            # Check if user is allowed for this request
            #if request.user.is_allowed(request):
            #    response = get_response(request)
            # response = get_response(request)

        response = get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware


class DebugJWTAuthentication(JWTAuthentication):
    """
        Authentication class used for debug purposes
    """

    def authenticate(self, request):
        """
            Authenticate the request and return a two-tuple of (user, token).

            :return: A two-tuple of (user, token).
            :rtype: tuple
        """
        # Get the Authentication header
        auth = get_authorization_header(request).split()

        if len(auth) == 0:
            return self.authenticate_credentials(None)

        return super().authenticate(request)

    def authenticate_credentials(self, token):
        """
            Check provided token and perform authentication

            :param token: The JWT token provided
            :type token: str
            :return: A two-tuple of (user, token).
            :rtype: tuple
        """
        if settings.DEBUG_AUTHENTICATION_OBJECT is None:
            return UnauthenticatedUser(), None

        obj_type = settings.DEBUG_AUTHENTICATION_OBJECT[0]

        payload = {
            "sub": settings.DEBUG_AUTHENTICATION_OBJECT[1],
            "pk": settings.DEBUG_AUTHENTICATION_OBJECT[1],
            "allowed_scopes": "",
            "filters": ""
        }
        if obj_type == "admin":
            payload['group'] = "users"
            payload['type'] = "admin"
        elif obj_type == "user":
            payload['group'] = "users"
            payload['type'] = "user"
        elif obj_type == "vle":
            payload['group'] = "module_vle_{}".format(payload['pk'])
            payload['type'] = "vle"
        elif obj_type == "provider":
            payload['group'] = "module_provider_{}".format(payload['pk'])
            payload['type'] = "provider"
        else:
            raise AuthenticationFailed(_('Invalid user credentials.'))

        if len(settings.DATABASES) > 0:
            user = self._get_user_model(payload)
        else:
            user = AuthenticatedUser()
            user.type = payload['type']
            user.allowed_scopes = payload['allowed_scopes']
            user.sub = payload['sub']
            user.pk = payload['pk']
            user.filters = payload['filters']

        return user, None
