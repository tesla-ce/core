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

from .activity import VLECourseActivityViewSet
from .activity_instrument import VLECourseActivityInstrumentViewSet
from .activity_report import VLECourseActivityReportViewSet
from .course import VLECourseViewSet
from .instructor import VLECourseInstructorViewSet
from .instrument import VLEInstrumentViewSet
from .learner import VLECourseActivityLearnerViewSet
from .learner import VLECourseLearnerViewSet
from .request import VLECourseActivityLearnerRequestViewSet
from .vle import VLEViewSet

__all__ = [
    "VLEViewSet",
    "VLECourseViewSet",
    "VLECourseActivityViewSet", "VLECourseActivityInstrumentViewSet", "VLECourseActivityReportViewSet",
    "VLECourseLearnerViewSet",
    "VLECourseActivityLearnerViewSet",
    "VLECourseInstructorViewSet",
    "VLECourseActivityLearnerRequestViewSet",
    "VLEInstrumentViewSet",
]
