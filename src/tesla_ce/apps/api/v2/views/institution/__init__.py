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
""" Institution views definition package"""
from .activity import InstitutionCourseActivityViewSet
from .activity_instrument import InstitutionCourseActivityInstrumentViewSet
from .activity_report import InstitutionCourseActivityReportViewSet
from .activity_report_audit import InstitutionCourseActivityReportAuditViewSet
from .course import InstitutionCourseViewSet
from .course_learner import InstitutionCourseLearnerViewSet
from .course_instructor import InstitutionCourseInstructorViewSet
from .course_group import InstitutionCourseGroupCourseViewSet
from .course_group import InstitutionCourseGroupViewSet
from .informed_consent import InstitutionInformedConsentViewSet
from .informed_consent_document import InstitutionInformedConsentDocumentViewSet
from .institution import InstitutionViewSet
from .instructor import InstitutionInstructorViewSet
from .instrument import InstitutionInstrumentViewSet
from .learner import InstitutionLearnerViewSet
from .request import InstitutionCourseActivityReportRequestViewSet
from .send_category import InstitutionSENDCategoryViewSet
from .send_learner import InstitutionSENDLearnerViewSet
from .ui_option import InstitutionUIOptionViewSet
from .user import InstitutionUserViewSet
from .vle import InstitutionVLEViewSet

__all__ = [
    "InstitutionViewSet",
    "InstitutionCourseActivityViewSet",
    "InstitutionCourseActivityReportViewSet",
    "InstitutionCourseActivityInstrumentViewSet",
    "InstitutionCourseViewSet",
    "InstitutionCourseGroupViewSet",
    "InstitutionCourseGroupCourseViewSet",
    "InstitutionLearnerViewSet",
    "InstitutionCourseActivityReportRequestViewSet",
    "InstitutionCourseActivityReportAuditViewSet",
    "InstitutionCourseLearnerViewSet",
    "InstitutionCourseInstructorViewSet",
    "InstitutionInstructorViewSet",
    "InstitutionInformedConsentViewSet",
    "InstitutionInformedConsentDocumentViewSet",
    "InstitutionSENDCategoryViewSet",
    "InstitutionSENDLearnerViewSet",
    "InstitutionVLEViewSet",
    "InstitutionUIOptionViewSet",
    "InstitutionUserViewSet",
    "InstitutionInstrumentViewSet",
]
