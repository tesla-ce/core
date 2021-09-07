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
from .activity import InstitutionCourseActivitySerializer
from .activity_instrument import InstitutionCourseActivityInstrumentSerializer
from .activity_report import InstitutionCourseActivityReportDetailSerializer
from .activity_report import InstitutionCourseActivityReportExtendedSerializer
from .activity_report import InstitutionCourseActivityReportLearnerSerializer
from .activity_report import InstitutionCourseActivityReportSerializer
from .activity_report_audit import InstitutionCourseActivityReportAuditSerializer
from .course import InstitutionCourseSerializer
from .course_group import InstitutionCourseGroupCourseSerializer
from .course_group import InstitutionCourseGroupSerializer
from .course_learner import InstitutionCourseLearnerSerializer
from .course_instructor import InstitutionCourseInstructorSerializer
from .informed_consent import InstitutionInformedConsentSerializer
from .informed_consent_document import InstitutionInformedConsentDocumentSerializer
from .institution import InstitutionSerializer
from .instructor import InstitutionInstructorSerializer
from .learner import InstitutionLearnerDetailSerializer
from .learner import InstitutionLearnerICBodySerializer
from .learner import InstitutionLearnerSerializer
from .request import InstitutionCourseActivityReportRequestSerializer
from .send_category import InstitutionSENDCategorySerializer
from .send_learner import InstitutionSENDLearnerSerializer
from .ui_option import InstitutionUIOptionSerializer
from .user import InstitutionUserSerializer
from .vle import InstitutionVLESerializer

__all__ = [
    "InstitutionSerializer",
    "InstitutionCourseSerializer",
    "InstitutionCourseActivitySerializer",
    "InstitutionCourseActivityReportSerializer",
    "InstitutionCourseActivityReportAuditSerializer",
    "InstitutionCourseActivityReportDetailSerializer",
    "InstitutionCourseActivityReportExtendedSerializer",
    "InstitutionCourseActivityReportLearnerSerializer",
    "InstitutionCourseActivityInstrumentSerializer",
    "InstitutionCourseGroupSerializer",
    "InstitutionCourseGroupCourseSerializer",
    "InstitutionCourseLearnerSerializer",
    "InstitutionLearnerSerializer",
    "InstitutionCourseInstructorSerializer",
    "InstitutionCourseActivityReportRequestSerializer",
    "InstitutionLearnerDetailSerializer",
    "InstitutionInstructorSerializer",
    "InstitutionInformedConsentSerializer",
    "InstitutionLearnerICBodySerializer",
    "InstitutionInformedConsentDocumentSerializer",
    "InstitutionSENDCategorySerializer",
    "InstitutionSENDLearnerSerializer",
    "InstitutionVLESerializer",
    "InstitutionUIOptionSerializer",
    "InstitutionUserSerializer",
]
