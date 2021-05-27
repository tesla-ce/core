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
""" Exception definition module"""
# Initialize Sentry Error tracker
import os

import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.django import DjangoIntegration

# Initialize the Sentry Error Tracker
if os.getenv('SENTRY_ENABLED') in ['1', 1, 'True', 'yes', 'true'] and os.getenv('SENTRY_DSN') is not None:
    sentry_sdk.init(
        os.getenv('SENTRY_DSN'),
        max_breadcrumbs=50,
        debug=os.getenv('DEBUG', '0') in ['1', 1, 'True', 'yes', 'true'],
        release=open(os.path.join(os.path.dirname(__file__), 'data', 'VERSION'), 'r').read(),
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
        integrations=[DjangoIntegration()],
        attach_stacktrace=True,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )


def tesla_report_exception(exception=None):
    """
        Send given exception to the Sentry Error Tracking system
        :param exception: Exception (optional)
        :return: Issue id or None if tracking is not enabled
    """
    if os.getenv('SENTRY_ENABLED') in ['1', 1, 'True', 'yes', 'true'] and os.getenv('SENTRY_DSN') is not None:
        return capture_exception(exception)
    return None


class TeslaException(Exception):
    """ Base class to raise exceptions """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        tesla_report_exception(self)


class TeslaConfigException(TeslaException):
    """ Class to raise configuration exceptions """
    pass


class TeslaVaultException(TeslaException):
    """ Class to raise vault related exceptions """
    pass


class TeslaAuthException(TeslaException):
    """ Class to raise authentication related exceptions """
    pass


class TeslaDatabaseException(TeslaException):
    """ Class to raise database related exceptions """
    pass


class TeslaDeploymentException(TeslaException):
    """ Class to raise deployment related exceptions """
    pass


class TeslaStorageException(TeslaException):
    """ Class to raise storage related exceptions """
    pass


class TeslaMissingICException(TeslaException):
    """ Class to raise exception when a learner does not have a valid informed consent """
    pass


class TeslaInvalidICException(TeslaException):
    """ Class to raise exception when a learner have an invalid informed consent """
    pass


class TeslaMissingEnrolmentException(TeslaException):
    """ Class to raise exception when required enrolments are missing """
    pass
