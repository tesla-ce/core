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
""" TeSLA User module """
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .institution import Institution


class BaseUser(BaseModel, User):
    """
        Base user for TeSLA CE.
    """
    locale = models.CharField(max_length=10, null=True, blank=False, default=None,
                              help_text=_('Default locale for this user'))
    created_at = models.DateTimeField(auto_now_add=True, help_text=_('Date when user was created'))
    updated_at = models.DateTimeField(auto_now=True, help_text=_('Last user modification'))

    def get_username(self):
        """
            Get the username of the user, corresponding to the email

            :return: User's username
            :rtype: str
        """
        return self.email

    def is_allowed(self, request):
        """
            Check if a request is allowed for current user, depending on the allowed scopes

            :return: Boolean value indicating if request is allowed for this user or not
        """
        for scope in self.allowed_scopes:
            if request.path.startswith(scope):
                return True
        return False

    @property
    def allowed_scopes(self):
        """
            Scopes the user is allowed to access

            :return: List of allowed scopes
            :rtype: list
        """
        return []

    class Meta:
        abstract = True

    def __repr__(self):
        return "<BaseUser(id='%r', email='%r', is_active='%r')>" % (
            self.id, self.email, self.is_active
        )


class UnauthenticatedUser(AnonymousUser):
    """
        Default user for unauthenticated requests
    """
    is_active = False

    def is_allowed(self, request):
        """
            Check if a request is allowed for current user, depending on the allowed scopes
            :return: Boolean value indicating if the user is authenticated or not
        """
        return False

    def __repr__(self):
        return "<UnauthenticatedUser>"


class AuthenticatedModule(AnonymousUser):
    """
        Default user for authenticated requests from modules
    """
    is_active = True
    module = None
    type = None

    def is_allowed(self, request):
        """
            Check if a request is allowed for current user, depending on the allowed scopes
            :return: Boolean value indicating if the user is authenticated or not
        """
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        return "<AuthenticatedModule(type='%r', module='%r')>" % (
            self.type, self.module
        )


class InstitutionUser(BaseUser):
    """
        User belonging to an institution
    """
    uid = models.CharField(max_length=255, null=False, blank=False,
                           help_text=_('Unique User Identifier for the institution'))
    institution = models.ForeignKey(Institution, null=False, on_delete=models.CASCADE,
                                    help_text=_('Institution of the user'))

    login_allowed = models.BooleanField(null=False, default=False,
                                        help_text=_('Whether this user can login with user/password'))

    inst_admin = models.BooleanField(null=False, default=False,
                                     help_text=_('Whether this user is administrator of the institution'))

    legal_admin = models.BooleanField(null=False, default=False,
                                      help_text=_('Whether this user can manage legal data of the institution'))

    send_admin = models.BooleanField(null=False, default=False,
                                     help_text=_('Whether this user can manage SEND data of the institution'))

    data_admin = models.BooleanField(null=False, default=False,
                                     help_text=_('Whether this user can manage the data of the institution'))

    class Meta:
        unique_together = (('institution', 'uid'),)


class AuthenticatedUser(AnonymousUser):
    """
        Default user for authenticated requests from JWT without DB access
    """
    is_active = True
    type = None
    allowed_scopes = None
    sub = None
    filters = None

    def is_allowed(self, request):
        """
            Check if a request is allowed for current user, depending on the allowed scopes
            :return: Boolean value indicating if the user is authenticated or not
        """
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return "<AuthenticatedUser(type='%r', sub='%r')>" % (
            self.type, self.sub
        )
