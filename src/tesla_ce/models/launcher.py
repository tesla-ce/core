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
""" Launcher model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .assessment_session import AssessmentSession
from .base_model import BaseModel
from .user import InstitutionUser

LAUNCHER_TARGET = (
    (0, _('Dashboard')),
    (1, _('LAPI')),
)


class Launcher(BaseModel):
    """ Launcher model. """
    user = models.ForeignKey(InstitutionUser, null=False,
                             on_delete=models.CASCADE,
                             help_text=_("Related user"))

    session = models.ForeignKey(AssessmentSession, null=True, default=None,
                                on_delete=models.SET_NULL,
                                help_text=_("Related assessment session"))

    target = models.IntegerField(choices=LAUNCHER_TARGET, null=False,
                                 default=0,
                                 help_text=_('Target for this launcher'))

    target_url = models.CharField(max_length=250, null=True, default=None,
                                  help_text=_('Url to redirect'))

    token = models.UUIDField(null=False, help_text=_("Token to allow authentication for this user"))

    token_pair = models.TextField(null=False, help_text=_('Pair of tokens to authenticate with target'))

    expires_at = models.DateTimeField(null=False,
                                      help_text=_("When this access token expires"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
