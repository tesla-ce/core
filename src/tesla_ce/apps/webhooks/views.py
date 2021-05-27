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
""" Webhooks views module """
from rest_framework.views import APIView
from rest_framework.views import Response
from rest_framework.views import status

from tesla_ce.apps.webhooks import exceptions
from .client.base import BaseWebhookMessage


class WebhooksView(APIView):
    """
        Receiver for webhooks
    """
    def post(self, request):
        """
            Webhook process

            :param request:
            :return:
        """
        try:
            msg = BaseWebhookMessage.get_webhook_object(request)
            msg.save()
            msg.process()
        except exceptions.WebhookAuthException as wae:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'message': wae.__str__()})
        except exceptions.WebhookClientNotFoundException as wcnfe:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': wcnfe.__str__()})
        except exceptions.WebhookException as we:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': we.__str__()})

        return Response(status=status.HTTP_200_OK)


class WebhooksEditView(APIView):
    """
        Webhooks edit view
    """

    def get(self, request, format=None, webhook_id=None):
        """
            Get webhook data

            :param request:
            :param webhook_id: Unique identifier for webhook
            :return:
        """
        msg_data = None
        try:
            msg = BaseWebhookMessage.load(webhook_id, request)
            msg_data = msg.get_data()
        except exceptions.WebhookAuthException as wae:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'message': wae.__str__()})
        except exceptions.WebhookClientNotFoundException as wcnfe:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': wcnfe.__str__()})
        except exceptions.WebhookException as we:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': we.__str__()})

        return Response(status=status.HTTP_200_OK, data=msg_data)

    def post(self, request, webhook_id=None):
        """
            Update webhook

            :param request:
            :param webhook_id: Unique identifier for webhook
            :return:
        """
        try:
            msg = BaseWebhookMessage.load(webhook_id, request)
            message = None
            status_val = None
            if "status" in request.data:
                status_val = request.data['status']
            if "message" in request.data:
                message = request.data['message']
            msg.update_status(status_val, message)
        except exceptions.WebhookAuthException as wae:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'message': wae.__str__()})
        except exceptions.WebhookClientNotFoundException as wcnfe:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': wcnfe.__str__()})
        except exceptions.WebhookException as we:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': we.__str__()})

        return Response(status=status.HTTP_200_OK)
