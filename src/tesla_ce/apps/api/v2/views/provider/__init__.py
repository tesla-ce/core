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
""" Providers views definition package"""
from .enrolment import ProviderEnrolmentViewSet
from .enrolment_sample import ProviderEnrolmentSampleViewSet
from .provider import ProviderViewSet
from .provider_notification import ProviderNotificationViewSet
from .request_provider_result import ProviderVerificationRequestResultViewSet
from .validation import ProviderEnrolmentSampleValidationViewSet

__all__ = [
    "ProviderViewSet",
    "ProviderEnrolmentViewSet",
    "ProviderEnrolmentSampleViewSet",
    "ProviderEnrolmentSampleValidationViewSet",
    "ProviderVerificationRequestResultViewSet",
    "ProviderNotificationViewSet",
]
