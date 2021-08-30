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

""" VLe nested serializers package """
from .activity import VLECourseActivitySerializer
from .activity_instrument import VLECourseActivityInstrumentSerializer
from .activity_report import VLECourseActivityReportExtendedSerializer
from .activity_report import VLECourseActivityReportSerializer
from .assessment_session import VLENewAssessmentSessionBodySerializer
from .assessment_session import VLENewAssessmentSessionSerializer
from .attachment import VLECourseActivityAttachmentSerializer
from .course import VLECourseSerializer
from .instructor import VLECourseInstructorSerializer
from .instruments import VLEInstrumentSerializer
from .launcher import VLELauncherBodySerializer
from .launcher import VLELauncherDataSerializer
from .learner import VLECourseActivityLearnerSerializer
from .learner import VLECourseLearnerSerializer
from .request import VLECourseActivityLearnerRequestSerializer
from .vle import VLESerializer

__all__ = [
    "VLESerializer",
    "VLECourseSerializer",
    "VLECourseActivitySerializer",
    "VLECourseActivityInstrumentSerializer",
    "VLECourseActivityAttachmentSerializer",
    "VLECourseLearnerSerializer",
    "VLECourseActivityLearnerSerializer",
    "VLECourseActivityLearnerRequestSerializer",
    "VLECourseInstructorSerializer",
    "VLENewAssessmentSessionSerializer",
    "VLENewAssessmentSessionBodySerializer",
    "VLECourseActivityReportSerializer",
    "VLECourseActivityReportExtendedSerializer",
    "VLEInstrumentSerializer",
    "VLELauncherBodySerializer",
    "VLELauncherDataSerializer",
]
