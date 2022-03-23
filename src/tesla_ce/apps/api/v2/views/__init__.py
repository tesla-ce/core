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
""" API views package """
from .admin import AdminProviderViewSet
from .admin import AdminUserViewSet
from .admin import InstitutionAdminViewSet
from .admin import InstrumentViewSet
from .admin import UIOptionViewSet
from .institution import InstitutionCourseActivityInstrumentViewSet
from .institution import InstitutionCourseActivityReportViewSet
from .institution import InstitutionCourseActivityReportAuditViewSet
from .institution import InstitutionCourseActivityViewSet
from .institution import InstitutionCourseGroupCourseViewSet
from .institution import InstitutionCourseGroupViewSet
from .institution import InstitutionCourseViewSet
from .institution import InstitutionInformedConsentDocumentViewSet
from .institution import InstitutionInformedConsentViewSet
from .institution import InstitutionInstructorViewSet
from .institution import InstitutionInstrumentViewSet
from .institution import InstitutionLearnerViewSet
from .institution import InstitutionCourseLearnerViewSet
from .institution import InstitutionCourseInstructorViewSet
from .institution import InstitutionCourseActivityReportRequestViewSet
from .institution import InstitutionSENDCategoryViewSet
from .institution import InstitutionSENDLearnerViewSet
from .institution import InstitutionUIOptionViewSet
from .institution import InstitutionUserViewSet
from .institution import InstitutionVLEViewSet
from .institution import InstitutionViewSet
from .provider import ProviderEnrolmentSampleValidationViewSet
from .provider import ProviderEnrolmentSampleViewSet
from .provider import ProviderEnrolmentViewSet
from .provider import ProviderNotificationViewSet
from .provider import ProviderVerificationRequestResultViewSet
from .provider import ProviderViewSet
from .vle import VLECourseActivityInstrumentViewSet
from .vle import VLECourseActivityLearnerRequestViewSet
from .vle import VLECourseActivityLearnerViewSet
from .vle import VLECourseActivityReportViewSet
from .vle import VLECourseActivityViewSet
from .vle import VLECourseInstructorViewSet
from .vle import VLECourseLearnerViewSet
from .vle import VLECourseViewSet
from .vle import VLEInstrumentViewSet
from .vle import VLEViewSet

__all__ = [
    # Administration nested views
    "InstitutionAdminViewSet",
    "InstrumentViewSet",
    "AdminProviderViewSet",
    "AdminUserViewSet",
    "UIOptionViewSet",
    # VLE nested views
    "VLEViewSet",
    "VLECourseViewSet",
    "VLECourseActivityViewSet",
    "VLECourseActivityInstrumentViewSet",
    "VLECourseActivityReportViewSet",
    "VLECourseLearnerViewSet",
    "VLECourseActivityLearnerViewSet",
    "VLECourseActivityLearnerRequestViewSet",
    "VLECourseInstructorViewSet",
    "VLEInstrumentViewSet",
    # Institution nested views
    "InstitutionViewSet",
    "InstitutionCourseViewSet",
    "InstitutionCourseGroupViewSet",
    "InstitutionCourseGroupCourseViewSet",
    "InstitutionCourseActivityViewSet",
    "InstitutionCourseActivityReportViewSet",
    "InstitutionCourseActivityReportAuditViewSet",
    "InstitutionCourseActivityInstrumentViewSet",
    "InstitutionLearnerViewSet",
    "InstitutionCourseLearnerViewSet",
    "InstitutionCourseInstructorViewSet",
    "InstitutionCourseActivityReportRequestViewSet",
    "InstitutionInstructorViewSet",
    "InstitutionInformedConsentViewSet",
    "InstitutionInformedConsentDocumentViewSet",
    "InstitutionSENDCategoryViewSet",
    "InstitutionSENDLearnerViewSet",
    "InstitutionVLEViewSet",
    "InstitutionUIOptionViewSet",
    "InstitutionUserViewSet",
    # Provider nested views
    "ProviderViewSet",
    "ProviderEnrolmentViewSet",
    "ProviderEnrolmentSampleViewSet",
    "ProviderEnrolmentSampleValidationViewSet",
    "ProviderVerificationRequestResultViewSet",
    "ProviderNotificationViewSet",
]
