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
import os
import tempfile


def test_generate_configuration(tesla_ce_system, config_mode_settings):

    from tesla_ce.lib.config import ConfigManager

    assert tesla_ce_system is not None

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the configuration file
        conf_file = os.path.join(tmp_dir, 'test_gen_config.cfg')
        tesla_ce_system.generate_configuration(conf_file, 'test_domain',
                                               deploy_external_services=False, deploy_moodle=False)

        # Read the configuration
        conf = ConfigManager(load_config=False)
        conf.load_file(conf_file)

        # Check expected values
        assert conf.config.get('TESLA_DOMAIN') == 'test_domain'
        assert conf.config.get('DJANGO_SECRET_KEY') is not None
        assert 'test_domain' in conf.config.get('DJANGO_ALLOWED_HOSTS')

        # Check services
        assert conf.config.get('DB_USER', None) is None
        assert conf.config.get('DB_PASSWORD', None) is None
        assert conf.config.get('VAULT_DB_HOST') is None
        assert conf.config.get('VAULT_DB_USER') is None
        assert conf.config.get('RABBITMQ_ERLANG_COOKIE') is None
        assert conf.config.get('RABBITMQ_ADMIN_USER') is None
        assert conf.config.get('RABBITMQ_ADMIN_PASSWORD') is None
        assert conf.config.get('STORAGE_ACCESS_KEY') is None
        assert conf.config.get('STORAGE_SECRET_KEY') is None

        # Check Moodle
        assert not conf.config.get('MOODLE_DEPLOY')
        assert conf.config.get('MOODLE_ADMIN_PASSWORD') is None
        assert conf.config.get('MOODLE_DB_HOST') is None
        assert conf.config.get('MOODLE_DB_PASSWORD') is None


def test_generate_configuration_with_services(tesla_ce_system, config_mode_settings):
    from tesla_ce.lib.config import ConfigManager

    assert tesla_ce_system is not None

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the configuration file
        conf_file = os.path.join(tmp_dir, 'test_gen_config2.cfg')
        tesla_ce_system.generate_configuration(conf_file, 'test_domain2',
                                               deploy_external_services=True, deploy_moodle=False)

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

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Generate the configuration file
        conf_file = os.path.join(tmp_dir, 'test_gen_config3.cfg')
        tesla_ce_system.generate_configuration(conf_file, 'test_domain3',
                                               deploy_external_services=False, deploy_moodle=True)

        # Read the configuration
        conf = ConfigManager(load_config=False)
        conf.load_file(conf_file)

        # Check expected values
        assert conf.config.get('TESLA_DOMAIN') == 'test_domain3'
        assert conf.config.get('DJANGO_SECRET_KEY') is not None
        assert 'test_domain3' in conf.config.get('DJANGO_ALLOWED_HOSTS')

        # Check services
        assert conf.config.get('DB_USER', None) is None
        assert conf.config.get('DB_PASSWORD', None) is None
        assert conf.config.get('VAULT_DB_HOST') is None
        assert conf.config.get('VAULT_DB_USER') is None
        assert conf.config.get('RABBITMQ_ERLANG_COOKIE') is None
        assert conf.config.get('RABBITMQ_ADMIN_USER') is None
        assert conf.config.get('RABBITMQ_ADMIN_PASSWORD') is None
        assert conf.config.get('STORAGE_ACCESS_KEY') is None
        assert conf.config.get('STORAGE_SECRET_KEY') is None

        # Check Moodle
        assert conf.config.get('MOODLE_DEPLOY')
        assert conf.config.get('MOODLE_ADMIN_PASSWORD') is not None
        assert conf.config.get('MOODLE_DB_HOST') is not None
        assert conf.config.get('MOODLE_DB_PASSWORD') is not None
