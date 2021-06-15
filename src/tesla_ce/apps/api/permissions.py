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
""" TeSLA API permissions module """
from rest_framework import permissions

from tesla_ce.models import InstitutionUser
from tesla_ce.models import User


def get_institution_user(user):
    """
        Return a InstitutionUser object if user belongs to an institution or None otherwise
        :param user: User object
        :return: The InstitutionUser object or None
    """
    if isinstance(user, InstitutionUser):
        return user

    if isinstance(user, User):
        try:
            return user.institutionuser
        except Exception:
            # If user has no institution this will fail
            return None


def is_global_admin(user):
    """
        Check if provided user is a Global Admin
        :param user: User object
        :return: True if it is a global admin or False otherwise
    """
    if isinstance(user, InstitutionUser):
        return user.user_ptr.is_staff

    if isinstance(user, User):
        return user.is_staff


class GlobalAdminPermission(permissions.BasePermission):
    """
        Global admins have read only permissions
    """
    def has_permission(self, request, view):
        return request.user.is_staff


class GlobalAdminReadOnlyPermission(GlobalAdminPermission):
    """
        Global admins have read only permissions
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)

        return False


class InstitutionMemberPermission(permissions.BasePermission):
    """
        Only members of the institution can access to the view
    """

    def _get_user_institution(self, request):

        if not request.user.is_authenticated:
            return None

        if isinstance(request.user, InstitutionUser):
            return request.user.institution

        if isinstance(request.user, User):
            try:
                return request.user.institutionuser.institution
            except Exception:
                return None

    def has_permission(self, request, view):

        institution = self._get_user_institution(request)

        if institution is None or not request.path.startswith('/api/{}/institution/{}/'.format(request.version,
                                                                                               institution.id)):
            return False
        return True


class InstitutionMemberReadOnlyPermission(InstitutionMemberPermission):
    """
        Only members of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False


class InstitutionAdminPermission(InstitutionMemberPermission):
    """
        Only admins of the institution can access to the view
    """
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if isinstance(request.user, InstitutionUser):
                return request.user.inst_admin
            else:
                return request.user.institutionuser.inst_admin

        return False


class InstitutionAdminReadOnlyPermission(InstitutionAdminPermission):
    """
        Only admins of the institution can access to the view in read only mode
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return False
