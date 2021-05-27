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
""" Provider model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base_model import BaseModel
from .instrument import Instrument


class Provider(BaseModel):
    """ Provider model. """
    instrument = models.ForeignKey(Instrument, null=True,
                                   on_delete=models.SET_NULL)
    name = models.CharField(max_length=250, null=False, blank=False,
                            help_text=_("Provider name."))

    description = models.TextField(null=True, blank=True, default=None,
                                   help_text=_("Provider description."))

    url = models.CharField(max_length=250, null=True, blank=False, default=None,
                           help_text=_("Provider url."))

    version = models.CharField(max_length=15, null=False, blank=False,
                               help_text=_("Provider version."))

    acronym = models.CharField(max_length=30, null=False, blank=False, unique=True,
                               help_text=_("Provider Acronym."))

    queue = models.CharField(max_length=50, null=False, blank=False, unique=True,
                             help_text=_("Queue where provider listens for requests."))

    enabled = models.BooleanField(null=False, blank=False, default=False,
                                  help_text=_("Whether this provider is enabled to be used"))

    allow_validation = models.BooleanField(null=False, blank=False, default=False,
                                           help_text="Whether this provider provides validation feature for data")

    validation_active = models.BooleanField(null=False, blank=False, default=False,
                                            help_text="Whether this provider will be used for validation")

    alert_below = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=4, default=None,
                                      help_text=_("Mark as alert for result values below this threshold."))

    warning_below = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=4, default=None,
                                        help_text=_("Mark as warning for result values below this threshold."))

    inverted_polarity = models.BooleanField(null=False, default=False,
                                            help_text=_('If enabled, good values are lower values'))

    image = models.CharField(max_length=250, null=False, blank=False,
                             help_text=_("Provider Docker image."))

    has_service = models.BooleanField(null=False, default=False,
                                      help_text=_('Whether this provider starts a service and must be balanced'))
    service_port = models.IntegerField(null=True, default=None,
                                       help_text=_('Port where service is listening'))

    options_schema = models.TextField(null=True, blank=True, default=None,
                                      help_text=_("Schema for provider options."))
    options = models.TextField(null=True, blank=True, default=None,
                               help_text=_("Provider options."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<Provider(name='%s', acronym='%s', enabled='%r', queue='%r', allow_validation='%r')>" % (
            self.name, self.acronym, self.enabled, self.queue, self.allow_validation,
        )
