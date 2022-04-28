#  Copyright (c) 2021 Xavier Baró
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
""" Default Webhook client for providers implementation """
import json
import hmac
import hashlib

from tesla_ce.models import Provider
from tesla_ce.lib.webhook.process import process_webhook_message
from .base import BaseWebhookMessage
from .. import exceptions


class DefaultProviderWebhookMessage(BaseWebhookMessage):

    def __init__(self, client, body, message_id=None, model=None):
        super().__init__(client, body, message_id, model)
        try:
            self.provider = Provider.objects.get(acronym=client.name)
        except Provider.DoesNotExist:
            raise exceptions.WebhookProviderNotFoundException('Provider with acronym {} not found'.format(client.name))

    def _is_authenticated(self, request, webhook_client):
        if request is None:
            return False

        if request.headers.get('TESLA-SIGN') is None:
            return False

        signature_request = request.headers['TESLA-SIGN']

        credentials = json.loads(webhook_client.credentials)
        secret = credentials['secret']

        signature = hmac.new(secret.encode('utf8'), json.dumps(request.data).encode('utf8'), digestmod=hashlib.sha512)
        signature_calculated = signature.hexdigest()

        if signature_request != signature_calculated:
            return False

        return True

    def _process_webhook(self):
        process_webhook_message(self.model.id, self.provider.id)
