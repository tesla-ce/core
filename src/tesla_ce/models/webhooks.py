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
""" Activity model module."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from tesla_ce.apps.api.utils import JSONField
from .base_model import BaseModel


class WebhookClient(BaseModel):
    """ Webhook clients model. """
    name = models.CharField(max_length=250, null=False, blank=False, unique=True,
                            help_text=_("Name that identifies the client."))

    client_header = models.CharField(max_length=250, null=False, blank=False, unique=True,
                                     help_text=_("Name of the request header used to identify the client."))

    id_header = models.CharField(max_length=250, null=True, blank=False, default=None,
                                 help_text=_("Name of the request header used to get the message id."))

    description = models.TextField(null=True, blank=True,
                                   help_text=_("Client description."))

    implementation = models.CharField(max_length=255, null=False, blank=True,
                                      help_text=_("Webhook implementation class."))

    enabled = models.BooleanField(null=None, blank=None, default=False,
                                  help_text=_("Whether this client is enabled or not"))

    credentials = models.TextField(null=False, blank=False,
                                   help_text=_("Client authentication credentials."))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return "<WebhookClient(id='%r', name='%r', enabled='%r')>" % (
            self.id, self.name, self.enabled)

    def get_credentials(self):
        """
            Returns the body of the message
            :return: The JSON body
            :rtype: dict
        """
        if self.body is not None:
            json_field = JSONField()
            return json_field.to_representation(self.body)

        return None

WEBHOOK_STATUS = (
    (0, _('Created')),
    (1, _('Processing')),
    (2, _('Processed')),
    (3, _('Error')),
    (4, _('Timeout')),
)


class WebhookMessage(BaseModel):
    """ Webhook message model. """
    client = models.ForeignKey(WebhookClient, null=False, on_delete=models.CASCADE)

    status = models.IntegerField(choices=WEBHOOK_STATUS, null=False,
                                 default=0,
                                 help_text=_('Status for this request'))
    message_id = models.CharField(max_length=250, null=False, blank=False,
                                  help_text=_("Message Id."))
    error = models.TextField(null=True, blank=True,
                             help_text=_("Error message."))
    body = models.TextField(null=False, blank=False,
                            help_text=_("Webhook message body."))
    start_process_at = models.DateTimeField(null=True, default=None,
                                            help_text=_('When the webhook started to be processed'))
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('client', 'message_id'),)

    def get_body(self):
        """
            Returns the body of the message
            :return: The JSON body
            :rtype: dict
        """
        if self.body is not None:
            json_field = JSONField()
            return json_field.to_representation(self.body)

        return None
