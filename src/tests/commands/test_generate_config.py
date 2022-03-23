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
#
""" Configuration file generation test module """
import mock
import os
import tempfile
import pytest

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError


def test_generate_configuration(tesla_ce_system, config_mode_settings):

    from tesla_ce.lib.config import ConfigManager

    assert tesla_ce_system is not None

    out = StringIO()
    err = StringIO()

    with mock.patch('tesla_ce.management.base.TeslaCommand.get_client', return_value=tesla_ce_system):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Generate the configuration file
            conf_file = os.path.join(tmp_dir, 'test_gen_config.cfg')
            with mock.patch('tesla_ce.management.base.TeslaConfigCommand.get_config_file', return_value=conf_file):
                # Generate the configuration file
                domain = 'test_domain'
                call_command(
                    'generate_config',
                    domain,
                    stdout=out,
                    stderr=err,
                    with_services=False,
                    local=True
                )

            # Read the configuration
            conf = ConfigManager(load_config=False)
            conf.load_file(conf_file)

            # Check expected values
            assert conf.config.get('TESLA_DOMAIN') == 'test_domain'
            assert conf.config.get('DJANGO_SECRET_KEY') is not None
            assert 'test_domain' in conf.config.get('DJANGO_ALLOWED_HOSTS')

            # Check Moodle
            assert not conf.config.get('MOODLE_DEPLOY')
            assert conf.config.get('MOODLE_ADMIN_PASSWORD') is None
            assert conf.config.get('MOODLE_DB_HOST') is None
            assert conf.config.get('MOODLE_DB_PASSWORD') is None


def test_generate_configuration_with_services(tesla_ce_system, config_mode_settings):
    from tesla_ce.lib.config import ConfigManager

    assert tesla_ce_system is not None

    out = StringIO()
    err = StringIO()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the configuration file
        conf_file = os.path.join(tmp_dir, 'test_gen_config2.cfg')
        with mock.patch('tesla_ce.management.base.TeslaConfigCommand.get_config_file', return_value=conf_file):
            # Generate the configuration file
            domain = 'test_domain2'
            call_command(
                'generate_config',
                domain,
                stdout=out,
                stderr=err,
                with_services=True,
                local=True
            )

        # Read the configuration
        conf = ConfigManager(load_config=False)
        conf.load_file(conf_file)

        # Check expected values
        assert conf.config.get('TESLA_DOMAIN') == 'test_domain2'
        assert conf.config.get('DJANGO_SECRET_KEY') is not None
        assert 'test_domain2' in conf.config.get('DJANGO_ALLOWED_HOSTS')

        # Check services
        assert conf.config.get('DB_USER', None) is not None
        assert conf.config.get('DB_PASSWORD', None) is not None
        assert conf.config.get('VAULT_DB_HOST') is not None
        assert conf.config.get('VAULT_DB_USER') is not None
        assert conf.config.get('RABBITMQ_ERLANG_COOKIE') is not None
        assert conf.config.get('RABBITMQ_ADMIN_USER') is not None
        assert conf.config.get('RABBITMQ_ADMIN_PASSWORD') is not None
        assert conf.config.get('STORAGE_ACCESS_KEY') is not None
        assert conf.config.get('STORAGE_SECRET_KEY') is not None

        # Check Moodle
        assert not conf.config.get('MOODLE_DEPLOY')
        assert conf.config.get('MOODLE_ADMIN_PASSWORD') is None
        assert conf.config.get('MOODLE_DB_HOST') is None
        assert conf.config.get('MOODLE_DB_PASSWORD') is None


def test_generate_configuration_with_moodle(tesla_ce_system, config_mode_settings):
    from tesla_ce.lib.config import ConfigManager

    assert tesla_ce_system is not None

    out = StringIO()
    err = StringIO()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the configuration file
        conf_file = os.path.join(tmp_dir, 'test_gen_config3.cfg')
        with mock.patch('tesla_ce.management.base.TeslaConfigCommand.get_config_file', return_value=conf_file):
            # Generate the configuration file
            domain = 'test_domain3'
            call_command(
                'generate_config',
                domain,
                stdout=out,
                stderr=err,
                with_services=True,
                with_moodle=True,
                local=True
            )

        # Read the configuration
        conf = ConfigManager(load_config=False)
        conf.load_file(conf_file)

        # Check expected values
        assert conf.config.get('TESLA_DOMAIN') == 'test_domain3'
        assert conf.config.get('DJANGO_SECRET_KEY') is not None
        assert 'test_domain3' in conf.config.get('DJANGO_ALLOWED_HOSTS')

        # Check Moodle
        assert conf.config.get('MOODLE_DEPLOY')
        assert conf.config.get('MOODLE_ADMIN_PASSWORD') is not None
        assert conf.config.get('MOODLE_DB_HOST') is not None
        assert conf.config.get('MOODLE_DB_PASSWORD') is not None


def test_generate_configuration_override(tesla_ce_system, config_mode_settings):
    from tesla_ce.lib.config import ConfigManager

    assert tesla_ce_system is not None

    out = StringIO()
    err = StringIO()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the configuration file
        conf_file = os.path.join(tmp_dir, 'test_gen_config4.cfg')
        with mock.patch('tesla_ce.management.base.TeslaConfigCommand.get_config_file', return_value=conf_file):
            # Generate the configuration file
            domain = 'test_domain4'
            call_command(
                'generate_config',
                domain,
                stdout=out,
                stderr=err,
                local=True
            )

        # Read the configuration
        conf = ConfigManager(load_config=False)
        conf.load_file(conf_file)

        # Check expected values
        assert conf.config.get('TESLA_DOMAIN') == 'test_domain4'
        assert conf.config.get('DJANGO_SECRET_KEY') is not None
        assert 'test_domain4' in conf.config.get('DJANGO_ALLOWED_HOSTS')

        with mock.patch('tesla_ce.management.base.TeslaConfigCommand.get_config_file', return_value=conf_file):
            # Generate again the configuration file without the override command
            domain = 'test_domain5'
            try:
                call_command(
                    'generate_config',
                    domain,
                    stdout=out,
                    stderr=err,
                    local=True
                )
                pytest.fail('Configuration file overrided')
            except CommandError:
                assert 'Use --override option' in out.getvalue()

        with mock.patch('tesla_ce.management.base.TeslaConfigCommand.get_config_file', return_value=conf_file):
            # Generate the configuration file
            domain = 'test_domain5'
            call_command(
                'generate_config',
                domain,
                stdout=out,
                stderr=err,
                override=True,
                local=True
            )

        # Read the configuration
        conf = ConfigManager(load_config=False)
        conf.load_file(conf_file)

        # Check expected values
        assert conf.config.get('TESLA_DOMAIN') == 'test_domain5'
        assert conf.config.get('DJANGO_SECRET_KEY') is not None
        assert 'test_domain5' in conf.config.get('DJANGO_ALLOWED_HOSTS')
