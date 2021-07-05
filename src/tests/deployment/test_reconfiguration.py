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
#
""" Swarm deployment scripts management tests """
import os
import tempfile

from io import StringIO

from django.core.management import call_command


def test_reconfigure(tesla_ce_system):

    assert tesla_ce_system is not None

    out = StringIO()
    err = StringIO()

    call_command(
        'reconfigure',
        stdout=out,
        stderr=err
    )
