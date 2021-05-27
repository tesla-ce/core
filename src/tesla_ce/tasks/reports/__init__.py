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
""" Reporting related tasks """
from .results import update_activity_report
from .results import update_course_report
from .results import update_learner_activity_instrument_report
from .results import update_learner_activity_report

__all__ = [
    "update_learner_activity_instrument_report",
    "update_learner_activity_report",
    "update_activity_report",
    "update_course_report",
]
