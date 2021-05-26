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
""" Webhook exceptions module """


class WebhookException(Exception):
    """
        Base Exception for webhooks
    """
    pass


class WebhookAuthException(WebhookException):
    """
        Exception raised when a webhook is not correctly authenticated
    """
    pass


class WebhookClientNotFoundException(WebhookException):
    """
        Exception raised when a webhook does not have any header matching enabled clients
    """
    pass


class WebhookMultipleClientsException(WebhookException):
    """
        Exception raised when a multiple matching enabled clients
    """
    pass


class WebhookProviderNotFoundException(WebhookException):
    """
        Exception raised when a webhook client does not have a valid linked provider
    """
    pass


class WebhookImplementationNotFoundException(WebhookException):
    """
        Exception raised when a client implementation class is not found
    """
    pass
