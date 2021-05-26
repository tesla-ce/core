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
from tesla_ce.models import Provider
from .base import BaseWebhookMessage
from .. import exceptions


class DefaultProviderWebhookMessage(BaseWebhookMessage):

    def __init__(self, client, body, message_id=None, model=None):
        super().__init__(client, body, message_id, model)
        try:
            self.provider = Provider.objects.get(acronym=client.name)
        except Provider.DoesNotExist:
            raise exceptions.WebhookProviderNotFoundException('Provider with acronym {} not found'.format(client.name))

    def _is_authenticated(self, request):
        return True

    def _process_webhook(self):
        print('PROCESSING MESSAGE')


