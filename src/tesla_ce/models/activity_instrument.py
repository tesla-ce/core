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
""" ActivityInstrument model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from tesla_ce.apps.api.utils import JSONField
from .activity import Activity
from .base_model import BaseModel
from .instrument import Instrument


class ActivityInstrument(BaseModel):
    """ ActivityInstrument model. """
    activity = models.ForeignKey(Activity, null=False, blank=False,
                                 on_delete=models.CASCADE,
                                 help_text=_('Activity.'),
                                 related_name='configuration')

    instrument = models.ForeignKey(Instrument, null=False, blank=False,
                                   on_delete=models.CASCADE,
                                   help_text=_('Activity.'))

    alternative_to = models.ForeignKey("ActivityInstrument", null=True, blank=False,
                                       on_delete=models.CASCADE,
                                       help_text=_('Primary instrument to be used.'))

    required = models.BooleanField(null=False, blank=False,
                                   help_text="Is instrument required?")

    active = models.BooleanField(null=False, blank=False,
                                 help_text="Is instrument active?")

    options = models.TextField(null=True, blank=True,
                               help_text="Instrument options?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_primary(self):
        """
            Whether this instrument is the primary option or is an alternative option
            :return: True if it is primary instrument
            :rtype: bool
        """
        return self.alternative_to is None

    @property
    def is_enabled(self):
        """
            Whether this instrument is enabled or not
            :return: True if it is enabled and false if it is disabled
            :rtype: bool
        """
        if self.active:
            return True
        if self.is_primary:
            return self.active

        return self.alternative_to.is_enabled

    def __repr__(self):
        return "<ActivityInstrument(activity_id='%r', instrument_id='%r', " \
               "is_primary='%r', required='%r', active='%r')>" % (
                   self.activity.id, self.instrument,
                   self.is_primary, self.required, self.active)

    def get_options(self):
        """
            Whether this instrument is the primary option or is an alternative option
            :return: True if it is primary instrument
            :rtype: bool
        """
        if self.options is not None:
            json_field = JSONField()
            return json_field.to_representation(self.options)

        return None
