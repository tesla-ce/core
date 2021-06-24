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
""" User Interface Options model module."""
from cache_memoize import cache_memoize

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .institution import Institution
from .user import InstitutionUser
from .user import get_institution_user
from .user import get_institution_roles
from .user import is_global_admin


@cache_memoize(24 * 60 * 60)
def get_role_base_ui_routes():
    """
        Compute the available routes for each role
        :return: List of allowed routes per role
        :rtype: dict
    """
    base_routes = UIOption.objects.filter(enabled=True,
                                          institution=None,
                                          roles=None
                                          ).values_list('route', flat=True)
    # Group each route by role
    routes = {
        '__all__': set(base_routes)
    }
    role_required_routes = UIOption.objects.filter(enabled=True,
                                                   institution=None,
                                                   roles__isnull=False
                                                   ).values_list('route', 'roles')
    for route, roles in role_required_routes:
        role_list = roles.split(',')
        for route_role in role_list:
            if route_role not in routes:
                routes[route_role] = set()
            routes[route_role].add(route)

    # Convert sets to lists to allow serialization
    for role in routes:
        routes[role] = list(routes[role])

    return routes


def get_user_ui_routes(user):
    """
        Compute the user interface options for a user

        :param user_id: The user id
        :type user_id: int
        :return: List of allowed routes
        :rtype: list
    """
    inst_user = get_institution_user(user)

    # Users not belonging to any institutions can see nothing unless are global_admins
    if inst_user is None and not is_global_admin(user):
        return []

    role_routes = get_role_base_ui_routes()
    routes = set(role_routes['__all__'])

    # Add routes for Global Admins
    if is_global_admin(user) and 'GLOBAL_ADMIN' in role_routes:
        routes = routes.union(set(role_routes['GLOBAL_ADMIN']))

    # If user has no institution, we can finish
    if inst_user is None:
        return list(routes)

    # Add routes for other roles
    for role in get_institution_roles(user):
        if role in role_routes:
            routes = routes.union(set(role_routes[role]))

    inst_blocked_routes = UIOption.objects.filter(institution=inst_user.institution,
                                                  enabled=False).values_list('route', flat=True)

    user_blocked_routes = UIOption.objects.filter(institution=inst_user.institution,
                                                  user=inst_user,
                                                  enabled=False).values_list('route', flat=True)

    allowed_routes = routes - set(inst_blocked_routes) - set(user_blocked_routes)

    return list(allowed_routes)


class UIOption(BaseModel):
    """ UI Option model. """
    route = models.CharField(max_length=250, null=False, blank=False, db_index=True,
                             help_text=_("Affected Route."))

    enabled = models.BooleanField(null=None, blank=None, default=False,
                                  help_text=_("Status"))

    institution = models.ForeignKey(Institution, null=True, on_delete=models.CASCADE, default=None,
                                    help_text=_('Affected institution'))

    user = models.ForeignKey(InstitutionUser, null=True, on_delete=models.CASCADE, default=None,
                             help_text=_('Affected user'))

    roles = models.CharField(max_length=250, null=True, blank=True,
                             help_text=_("Required roles."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<UIOption(id='%r', route='%r', enabled='%r', user='%r', institution='%r')>" % (
            self.id, self.route, self.enabled, self.user, self.institution)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        # Invalidate cached value
        if self.institution is None:
            get_role_base_ui_routes.invalidate()
