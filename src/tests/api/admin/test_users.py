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
""" Tests for users administration """
import pytest

from tests.conftest import get_random_string

from tests import auth_utils


@pytest.mark.django_db
def test_api_admin_user(user_global_admin, institution_test_case):
    """
        CRUD for users without institution
    """
    pytest.skip('TODO')


@pytest.mark.django_db
def test_api_admin_institution_user(user_global_admin, institution_test_case):
    """
        CRUD for users with institution
    """
    pytest.skip('TODO')


@pytest.mark.django_db
def test_api_admin_user_mix(user_global_admin, institution_test_case):
    """
        Test the transformation of users from institution to global and opposite
    """
    # Get a client with global administration rights
    pytest.skip('TODO')

