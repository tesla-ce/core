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
""" TeSLA CE scenario definition for Use Case tests """
from typing import List, Optional
from tesla_ce import models


class Activity:
    """
        Class defining a test activity
    """
    instruments = []


class Course:
    """
        Class defining a test course
    """
    # List of learners
    learners = []
    # List of instructors
    instructors = []


class Institution:
    """
        Class defining an institution
    """
    # Institution admin
    institution_admin: Optional[bool] = None
    # Institution SEND admin
    institution_send_admin: Optional[bool] = None
    # Institution Data admin
    institution_data_admin: Optional[bool] = None
    # Institution Legal admin
    institution_legal_admin: Optional[bool] = None
    # List of courses
    courses: List[Course] = []


class Context:
    """
        Define a test context
    """
    # Global admin
    global_admin: Optional[models.user.User] = None
    # Institution
    institutions: List[Institution] = []
    # Instruments

    def __init__(self, **kwargs):
        """
            Context constructor
        """
        pass


class UseCaseScenario:
    """
        Class defining a test scenario
    """
    # Current context
    current_context: Context = Context()
    # Expected context
    expected_context: Context = Context()

    def __init__(self, global_admin, **kwargs):
        """
            Scenario constructor
        """
        self.current_context.global_admin = global_admin
        self.expected_context.global_admin = global_admin

    def get_global_admin(self) -> Optional[models.user.User]:
        """
            Get the global admin user
            :return: Global admin user
        """
        return self.current_context.global_admin

    def check_global_admin(self):
        """
            Check that global admin is the expected
        """
        return self.current_context.global_admin.id == self.expected_context.global_admin.id
