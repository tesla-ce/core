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
import mock

from io import StringIO

from django.core.management import call_command
import pytest


def test_swarm_services_deployment(tesla_ce_system):

    pytest.skip('TODO')

    out = StringIO()
    err = StringIO()

    # If local configuration file is not available, generate configuration
    if not os.path.exists('tesla-ce.cfg'):
        assert tesla_ce_system.config.get('VAULT_TOKEN') is not None
        # Write the configuration file to disk
        with open('tesla-ce.cfg', 'w') as out_fh:
            tesla_ce_system.config.config.write(out_fh)
    else:
        from tesla_ce.lib.config import ConfigManager
        conf = ConfigManager(load_config=False)
        conf.load_file('tesla-ce.cfg')
        assert conf.config.get('VAULT_TOKEN') is not None

    # Enable with services flag
    deploy_services = tesla_ce_system.config.config.get('DEPLOYMENT_SERVICES')
    tesla_ce_system.config.config.set('DEPLOYMENT_SERVICES', True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        assert tmp_dir is not None
        with mock.patch('tesla_ce.management.base.TeslaCommand.get_client', return_value=tesla_ce_system):
            call_command(
                'deploy_services',
                stdout=out,
                stderr=err,
                out=tmp_dir,
                mode='swarm'
            )

        gen_files = os.listdir(tmp_dir)

        assert 'secrets' in gen_files
        assert os.path.isdir(os.path.join(tmp_dir, 'secrets'))
        assert len(os.listdir(os.path.join(tmp_dir, 'secrets'))) > 0

        assert 'config' in gen_files
        assert os.path.isdir(os.path.join(tmp_dir, 'secrets'))
        assert len(os.listdir(os.path.join(tmp_dir, 'secrets'))) > 0

    assert 'tesla_lb.yml' in gen_files
    assert 'tesla_services.yml' in gen_files
    tesla_ce_system.config.config.set('DEPLOYMENT_SERVICES', deploy_services)


def test_swarm_core_deployment(tesla_ce_system):

    out = StringIO()
    err = StringIO()

    # If local configuration file is not available, generate configuration
    if not os.path.exists('tesla-ce.cfg'):
        assert tesla_ce_system.config.get('VAULT_TOKEN') is not None
        # Write the configuration file to disk
        with open('tesla-ce.cfg', 'w') as out_fh:
            tesla_ce_system.config.config.write(out_fh)
    else:
        from tesla_ce.lib.config import ConfigManager
        conf = ConfigManager(load_config=False)
        conf.load_file('tesla-ce.cfg')
        assert conf.config.get('VAULT_TOKEN') is not None

    with mock.patch('tesla_ce.management.base.TeslaCommand.get_client', return_value=tesla_ce_system):
        with tempfile.TemporaryDirectory() as tmp_dir:
            call_command(
                'deploy_core',
                stdout=out,
                stderr=err,
                out=tmp_dir,
                mode='swarm'
            )

            gen_files = os.listdir(tmp_dir)

            assert 'secrets' in gen_files
            assert os.path.isdir(os.path.join(tmp_dir, 'secrets'))
            assert len(os.listdir(os.path.join(tmp_dir, 'secrets'))) > 0

        assert 'tesla_lb.yml' in gen_files
        assert 'tesla_core.yml' in gen_files
