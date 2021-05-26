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
""" Monitoring status model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel

RESOURCE_TYPE = (
    (0, _('Custom')),
    (1, _('Queue')),
    (2, _('Service')),
    (3, _('Provider')),
    (4, _('Instrument')),
)

RESOURCE_STATUS = (
    (0, _('Unknown')),
    (1, _('Ready')),
    (2, _('Error')),
    (3, _('Warning')),
)


class Monitor(BaseModel):
    """ Monitor status model. """
    status = models.IntegerField(choices=RESOURCE_STATUS, null=False,
                                 default=0,
                                 help_text=_('Status of the resource'))

    type = models.IntegerField(choices=RESOURCE_TYPE, null=False,
                               default=0,
                               help_text=_('Type of the resource'))

    key = models.CharField(max_length=15, null=True, default=None, blank=False,
                           help_text=_('key of the resource'))

    info = models.TextField(null=False, blank=False, help_text=_("Resource information."))

    created_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return "<Monitor(status='%r', type='%r', key='%r')>" % (
            self.get_status_display(), self.get_type_display(), self.key
        )
