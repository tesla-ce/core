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
""" Notifications for providers model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .provider import Provider


class ProviderNotification(BaseModel):
    """ Provider notification model. """
    provider = models.ForeignKey(Provider, null=False,
                                on_delete=models.CASCADE,
                                help_text=_("Related provider"))

    key = models.CharField(max_length=250, null=False,
                           help_text=_("Notification unique key for the provider"))

    info = models.TextField(null=True, blank=False, help_text=_("Notification information."))
    when = models.DateTimeField(null=False, help_text=_('When the notification should be sent to provider.'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('provider', 'key'),)

    def __repr__(self):
        return "<ProviderNotification(provider='%s', key='%r', when='%r')>" % (
            self.provider, self.key, self.info
        )
