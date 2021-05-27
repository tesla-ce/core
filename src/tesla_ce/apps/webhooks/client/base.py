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
""" Base Webhook client implementation """
import abc
import importlib

from django.utils import timezone

from tesla_ce.models import WebhookClient
from tesla_ce.models import WebhookMessage
from .. import exceptions


class BaseWebhookMessage:
    def __init__(self, client, body, message_id=None, model=None):
        self.body = body
        self.message_id = message_id
        self.client = client
        self.model = model

    @staticmethod
    def _get_class(implementation_class):
        implementation_class_parts = implementation_class.split('.')
        module_name = '.'.join(implementation_class_parts[:-1])
        class_name = implementation_class_parts[-1]

        module = importlib.import_module(module_name)
        try:
            imp_class = getattr(module, class_name)
        except Exception:
            raise exceptions.WebhookImplementationNotFoundException(
                'Invalid implementation class: {}'.format(implementation_class)
            )

        return imp_class

    @staticmethod
    def get_webhook_objects(request):
        # Get the list of client headers
        headers = [header.upper() for header in request.headers]
        clients = WebhookClient.objects.filter(enabled=True, client_header__in=headers).all()
        if len(clients) == 0:
            raise exceptions.WebhookClientNotFoundException('No client found for this request')
        objects = []
        for client in clients:
            message_id = None
            if client.id_header is not None and client.id_header in headers:
                message_id = request.headers[client.id_header]
            imp_class = BaseWebhookMessage._get_class(client.implementation)
            obj = imp_class(client, request.data, message_id)
            obj.authenticate(request)
            objects.append(obj)

        return objects

    @staticmethod
    def get_webhook_object(request):
        """
            Get a client object from request
            :param request: The HTTP request with webhook message
            :return: BaseCle
        """

        # Get the list of clients for current request
        clients = BaseWebhookMessage.get_webhook_objects(request)

        if clients is None:
            return None
        if len(clients) > 1:
            raise exceptions.WebhookMultipleClientsException('Multiple clients for given request')

        return clients[0]

    @abc.abstractmethod
    def _process_webhook(self):
        raise NotImplemented('Specific webhook process is not implemented')

    @abc.abstractmethod
    def _is_authenticated(self, request):
        raise NotImplemented('Specific webhook process is not implemented')

    def process(self):
        self.model.status = 1
        self.model.start_process_at = timezone.now()
        self.save()
        try:
            self._process_webhook()
        except Exception as exc:
            self.update_status(3, exc.__str__())

    def authenticate(self, request):
        if not self._is_authenticated(request):
            raise exceptions.WebhookAuthException('Invalid authentication')

    @staticmethod
    def load(pk, request=None):
        try:
            model = WebhookMessage.objects.get(pk=pk)
        except WebhookMessage.DoesNotExist:
            return None
        imp_class = BaseWebhookMessage._get_class(model.client.implementation)
        obj = imp_class(model.client, model.body, model.message_id, model)
        if request is not None:
            obj.authenticate(request)
        return obj

    def save(self):
        if self.model is None:
            self.model = WebhookMessage.objects.create(
                status=0,
                message_id=self.message_id,
                client=self.client,
                body=self.body
            )
        else:
            self.model.save()

    def get_data(self):
        if self.model is None:
            return None
        return self.model.get_body()

    def update_status(self, status, message):
        self.model.status = status
        self.model.error = message
        self.save()
