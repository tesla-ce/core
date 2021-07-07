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
""" Reconfiguration script management tests """
import os
from io import StringIO

from django.core.management import call_command


def test_reconfigure(tesla_ce_system):

    assert tesla_ce_system is not None

    out = StringIO()
    err = StringIO()

    # If local configuration file is not available, generate configuration
    if not os.path.exists('tesla-ce.cfg'):
        # Write the configuration file to disk
        with open('tesla-ce.cfg', 'w') as out_fh:
            tesla_ce_system.config.config.write(out_fh)

    call_command(
        'reconfigure',
        stdout=out,
        stderr=err,
        local=True
    )
