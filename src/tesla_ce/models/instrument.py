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
""" Instrument model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel


class Instrument(BaseModel):
    """ Instrument model. """
    name = models.CharField(max_length=250, null=False, blank=False,
                            help_text=_("Instrument name."))

    acronym = models.CharField(max_length=30, null=False, blank=False, unique=True,
                               help_text=_("Instrument Acronym."))

    queue = models.TextField(null=False, blank=False, unique=True,
                             help_text=_("Queue this instrument listens to."))

    enabled = models.BooleanField(null=False, blank=False, default=False,
                                  help_text=_("The instrument is enabled"))

    requires_enrolment = models.BooleanField(null=False, blank=False, default=False,
                                             help_text=_("Whether this instrument requires enrolment"))

    description = models.TextField(null=True, blank=True, default=None,
                                   help_text=_("Description of the instrument."))

    identity = models.BooleanField(null=False, blank=False, default=False,
                                   help_text=_("This instrument contributes to the learner identity verification"))
    originality = models.BooleanField(null=False, blank=False, default=False,
                                      help_text=_(
                                          "This instrument contributes to the assessment originality verification"))
    authorship = models.BooleanField(null=False, blank=False, default=False,
                                     help_text=_(
                                         "This instrument contributes to the assessment authorship verification"))
    integrity = models.BooleanField(null=False, blank=False, default=False,
                                    help_text=_(
                                         "This instrument contributes to the assessment integrity verification"))
    options_schema = models.TextField(null=True, blank=False, default=None,
                                      help_text=_("Schema for instrument options"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<Instrument(id='%d', name='%s', acronym='%s', queue='%s', enabled='%r')>" % (
            self.id, self.name, self.acronym, self.queue, self.enabled)

    @property
    def is_active(self):
        """
            Whether the instrument is active. This means that is enabled and have enabled providers.

            :return: True if the instrument is active or false otherwise
            :rtype: bool
        """
        return self.enabled and self.provider_set.filter(enabled=True).count() > 0
