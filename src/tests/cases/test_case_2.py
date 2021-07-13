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
""" TeSLA CE Activity use case test """
import pytest

from .utils.scenario import UseCaseScenario


@pytest.mark.django_db(transaction=False)
def test_activity_case_complete(rest_api_client, user_global_admin):
    """
        Complete example from institution creation to activity reports generation

        :param rest_api_client: Fixture that ensures that whole system is ready to use
        :param user_global_admin: Global administrator object
    """
    # Create an empty scenario with only the global user
    scenario = UseCaseScenario(
        global_admin = user_global_admin
    )
    assert scenario.get_global_admin() is not None
    assert scenario.check_global_admin()

