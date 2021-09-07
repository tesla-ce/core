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
""" API serializers package """
from .admin import InstitutionAdminSerializer
from .admin import InstrumentSerializer
from .admin import ProviderSerializer
from .admin import UIOptionSerializer
from .admin import UserSerializer
from .institution import InstitutionCourseActivityInstrumentSerializer
from .institution import InstitutionCourseActivityReportDetailSerializer
from .institution import InstitutionCourseActivityReportExtendedSerializer
from .institution import InstitutionCourseActivityReportLearnerSerializer
from .institution import InstitutionCourseActivityReportSerializer
from .institution import InstitutionCourseActivityReportAuditSerializer
from .institution import InstitutionCourseActivitySerializer
from .institution import InstitutionCourseGroupCourseSerializer
from .institution import InstitutionCourseGroupSerializer
from .institution import InstitutionCourseSerializer
from .institution import InstitutionInformedConsentDocumentSerializer
from .institution import InstitutionInformedConsentSerializer
from .institution import InstitutionInstructorSerializer
from .institution import InstitutionLearnerDetailSerializer
from .institution import InstitutionLearnerICBodySerializer
from .institution import InstitutionLearnerSerializer
from .institution import InstitutionSENDCategorySerializer
from .institution import InstitutionSENDLearnerSerializer
from .institution import InstitutionSerializer
from .institution import InstitutionCourseActivityReportRequestSerializer
from .institution import InstitutionCourseLearnerSerializer
from .institution import InstitutionCourseInstructorSerializer
from .institution import InstitutionUIOptionSerializer
from .institution import InstitutionUserSerializer
from .institution import InstitutionVLESerializer
from .provider import ProviderEnrolmentSampleSerializer
from .provider import ProviderEnrolmentSampleValidationSerializer
from .provider import ProviderEnrolmentSerializer
from .provider import ProviderNotificationSerializer
from .provider import ProviderVerificationRequestResultSerializer
from .vle import VLECourseActivityInstrumentSerializer
from .vle import VLECourseActivityLearnerRequestSerializer
from .vle import VLECourseActivityLearnerSerializer
from .vle import VLECourseActivityReportExtendedSerializer
from .vle import VLECourseActivityReportSerializer
from .vle import VLECourseActivitySerializer
from .vle import VLECourseActivityAttachmentSerializer
from .vle import VLECourseInstructorSerializer
from .vle import VLECourseLearnerSerializer
from .vle import VLECourseSerializer
from .vle import VLEInstrumentSerializer
from .vle import VLELauncherBodySerializer
from .vle import VLELauncherDataSerializer
from .vle import VLENewAssessmentSessionBodySerializer
from .vle import VLENewAssessmentSessionSerializer
from .vle import VLESerializer

__all__ = [
    # Administration nested serializers
    "InstitutionAdminSerializer",
    "InstrumentSerializer",
    "ProviderSerializer",
    "UIOptionSerializer",
    "UserSerializer",
    # VLE nested serializers
    "VLESerializer",
    "VLECourseSerializer",
    "VLECourseActivitySerializer",
    "VLECourseActivityInstrumentSerializer",
    "VLECourseLearnerSerializer",
    "VLECourseActivityLearnerSerializer",
    "VLECourseActivityLearnerRequestSerializer",
    "VLECourseActivityAttachmentSerializer",
    "VLECourseInstructorSerializer",
    "VLENewAssessmentSessionSerializer",
    "VLENewAssessmentSessionBodySerializer",
    "VLECourseActivityReportSerializer",
    "VLECourseActivityReportExtendedSerializer",
    "VLEInstrumentSerializer",
    "VLELauncherBodySerializer",
    "VLELauncherDataSerializer",
    # Institution nested serializers
    "InstitutionSerializer",
    "InstitutionCourseActivitySerializer",
    "InstitutionCourseActivityReportSerializer",
    "InstitutionCourseActivityReportAuditSerializer",
    "InstitutionCourseActivityReportDetailSerializer",
    "InstitutionCourseActivityReportExtendedSerializer",
    "InstitutionCourseActivityReportLearnerSerializer",
    "InstitutionCourseActivityInstrumentSerializer",
    "InstitutionCourseActivityInstrumentSerializer",
    "InstitutionCourseSerializer",
    "InstitutionCourseGroupSerializer",
    "InstitutionCourseGroupCourseSerializer",
    "InstitutionCourseLearnerSerializer",
    "InstitutionCourseInstructorSerializer",
    "InstitutionLearnerSerializer",
    "InstitutionCourseActivityReportRequestSerializer",
    "InstitutionInstructorSerializer",
    "InstitutionLearnerDetailSerializer",
    "InstitutionLearnerICBodySerializer",
    "InstitutionInformedConsentSerializer",
    "InstitutionInformedConsentDocumentSerializer",
    "InstitutionSENDCategorySerializer",
    "InstitutionSENDLearnerSerializer",
    "InstitutionVLESerializer",
    "InstitutionUIOptionSerializer",
    "InstitutionUserSerializer",
    # Provider nested serializers
    "ProviderEnrolmentSerializer",
    "ProviderEnrolmentSampleSerializer",
    "ProviderEnrolmentSampleValidationSerializer",
    "ProviderVerificationRequestResultSerializer",
    "ProviderNotificationSerializer",
]
