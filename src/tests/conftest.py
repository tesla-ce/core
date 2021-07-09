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
""" Test fixtures module """
import json
import os
import random
import string

import pytest
from django.conf import settings
from django.utils import timezone

from tesla_ce.client import Client
from tesla_ce.client import ConfigManager
from tesla_ce.models import Provider


def get_random_string(length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for idx in range(length))


@pytest.fixture(scope='session')
def django_db_setup():
    # Disable automatic database configuration
    pass


def create_module_client(client, module):
    assert client is not None
    credentials = client.vault.get_module_credentials(module)
    assert 'role_id' in credentials and 'secret_id' in credentials
    config = ConfigManager(load_config=False)
    config.config.set('VAULT_SSL_VERIFY', client.config.config.get('VAULT_SSL_VERIFY'))
    config.load_vault(vault_url=client.config.config.get('VAULT_URL'),
                      role_id=credentials['role_id'],
                      secret_id=credentials['secret_id'])
    return Client(config=config)


@pytest.mark.django_db
def get_provider_object(api_client, desc_file):
    """
        Register a provider from a description file
        :param api_client: API client object
        :param desc_file: Path to the description file
        :return: Provider object
    """
    with open(desc_file, 'r') as info_file:
        provider_info = json.load(info_file)
    api_client.register_provider(provider_info)

    provider = Provider.objects.get(acronym=provider_info['acronym'])

    return provider


@pytest.fixture
def providers(api_client, db):
    tfr_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', '..', 'providers', 'fr_tfr.json'))
    tfa_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', '..', 'providers', 'fa_tfa.json'))
    tpt_file = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            '..', '..', 'providers', 'pt_tpt.json'))

    provider_obj = {
        'fr': get_provider_object(api_client, tfr_file),
        'fa': get_provider_object(api_client, tfa_file),
        'plag': get_provider_object(api_client, tpt_file),
    }

    return provider_obj


@pytest.fixture(scope="session", autouse=True)
def tesla_ce_system(django_db_blocker):
    """
        Initialize the TeSLA client.

        :return: TeSLA Client with Administration credentials
    """
    with django_db_blocker.unblock():
        client = Client(enable_management=True)
        report = client.check_configuration()
        print(json.dumps(report))
        assert report['valid']
        client.initialize()

        # Remove Vault Token from environment if present
        if 'VAULT_TOKEN' in os.environ:
            del os.environ['VAULT_TOKEN']

        yield client


@pytest.fixture
def admin_client(tesla_ce_system):
    """
        Initialize the TeSLA client.

        :return: TeSLA Client with Administration credentials
    """
    # Generate credentials for API and LAPI
    credentials_api = tesla_ce_system.vault.get_module_credentials('api')
    credentials_lapi = tesla_ce_system.vault.get_module_credentials('lapi')
    role_id = [credentials_api['role_id'], credentials_lapi['role_id']]
    secret_id = [credentials_api['secret_id'], credentials_lapi['secret_id']]

    config = ConfigManager(load_config=False)
    config.config.set('VAULT_SSL_VERIFY', tesla_ce_system.config.config.get('VAULT_SSL_VERIFY'))
    config.load_vault(vault_url=tesla_ce_system.config.config.get('VAULT_URL'),
                      role_id=role_id,
                      secret_id=secret_id,
                      approle_path=tesla_ce_system.config.config.get('VAULT_MOUNT_PATH_APPROLE'),
                      kv_path=tesla_ce_system.config.config.get('VAULT_MOUNT_PATH_KV')
                      )
    settings.TESLA_CONFIG=config
    settings.TESLA_MODULES=config.enabled_modules

    yield tesla_ce_system


@pytest.fixture
def api_client(admin_client):
    return create_module_client(admin_client, 'api')


@pytest.fixture
def lapi_client(admin_client):
    return create_module_client(admin_client, 'lapi')


@pytest.fixture
def rest_api_client(admin_client, monkeypatch):
    from rest_framework.test import APIClient
    client = APIClient()
    return client


@pytest.fixture
def user_global_admin(db):
    """
        Get a user with Global Administration privileges

        :return: User with Global Admin privileges
    """
    from tesla_ce.models import User

    admin = User.objects.filter(is_staff=True).all()
    if len(admin) == 0:
        admin = User.objects.create_user('test_admin', 'test_admin@tesla-ce.eu', is_staff=True, is_active=True)
    else:
        admin = admin[0]

    yield admin


@pytest.fixture
def institution_test_case(db):
    """
        Get a test institution with one user

        :return: Dictionary with institution and user
    """
    from tesla_ce.models import Institution, InstitutionUser

    # Create a test institution
    test_inst = Institution.objects.create(
        name="PyTest Test institution",
        acronym=get_random_string(10)
    )

    # Create a user for this institution
    user_name = get_random_string(10)
    test_user = InstitutionUser.objects.create(
        username=user_name,
        uid=user_name,
        email='{}@tesla-ce.eu'.format(user_name),
        first_name=user_name[:5],
        last_name=user_name[5:],
        institution=test_inst,
        login_allowed=False,
    )

    yield {
        'institution': test_inst,
        'user': test_user.user_ptr
    }


@pytest.fixture
def institution_course_test_case(db, admin_client, institution_test_case):
    """
        Get a test institution with one user, one course and users

        :return: Dictionary with institution and user
    """
    from tesla_ce.models import Course, InstitutionUser, Instructor, Learner, VLE

    # Create a VLE
    vle_name = get_random_string(10)
    admin_client.register_vle(
        type='moodle',
        name=vle_name,
        url='{}.tesla-ce-eu'.format(vle_name),
        institution_acronym=institution_test_case['institution'].acronym,
        client_id=get_random_string(15)
    )
    test_vle = VLE.objects.get(name=vle_name)

    # Create a test course
    test_course = Course.objects.create(
        code=get_random_string(10),
        description="PyTest test course",
        vle=test_vle,
        vle_course_id=get_random_string(5)
    )

    # Create an instructor
    instructor_user_name = get_random_string(10)
    test_instructor_usr = InstitutionUser.objects.create(
        username=instructor_user_name,
        uid=instructor_user_name,
        email='{}@tesla-ce.eu'.format(instructor_user_name),
        first_name=instructor_user_name[:5],
        last_name=instructor_user_name[5:],
        institution=institution_test_case['institution'],
        login_allowed=False,
    )
    test_instructor = Instructor(
        institutionuser_ptr=test_instructor_usr,
        institution=institution_test_case['institution']
    )
    test_instructor.save_base(raw=True)
    test_instructor = Instructor.objects.get(id=test_instructor_usr.id)
    test_course.instructors.add(test_instructor)

    # Create a learner
    learner_user_name = get_random_string(10)
    test_learner_usr = InstitutionUser.objects.create(
        username=learner_user_name,
        uid=learner_user_name,
        email='{}@tesla-ce.eu'.format(learner_user_name),
        first_name=learner_user_name[:5],
        last_name=learner_user_name[5:],
        institution=institution_test_case['institution'],
        login_allowed=False,
    )
    test_learner = Learner(
        institutionuser_ptr=test_learner_usr,
        institution=institution_test_case['institution'],
        joined_at=timezone.now()
    )
    test_learner.save_base(raw=True)
    test_learner = Learner.objects.get(id=test_learner_usr.id)
    test_course.learners.add(test_learner)

    institution_test_case['vle'] = test_vle
    institution_test_case['course'] = test_course
    institution_test_case['instructor'] = test_instructor.user_ptr
    institution_test_case['learner'] = test_learner.user_ptr

    yield institution_test_case


@pytest.fixture()
def config_mode_settings(settings):
    """
        Initialize the TeSLA client.

        :return: TeSLA Client with Administration credentials
    """
    settings.TESLA_CONFIG.config.set('TESLA_MODE', 'config')


@pytest.fixture
def empty_ui_routes(db):
    """
        Remove all UI Options routes
    """
    from tesla_ce.models import UIOption
    UIOption.objects.all().delete()

    yield []


@pytest.fixture
def base_ui_routes(db, empty_ui_routes):
    """
        Get a test institution with one user, one course and users

        :return: Dictionary with institution and user
    """
    from tesla_ce.models import UIOption
    routes = []
    # Administration route
    routes.append('/admin')
    UIOption.objects.create(route='/admin', enabled=True, roles='GLOBAL_ADMIN')
    # Dashboard route
    routes.append('/dashboard')
    UIOption.objects.create(route='/dashboard', enabled=True)
    # MyCourses route
    routes.append('/mycourses')
    UIOption.objects.create(route='/mycourses', enabled=True, roles='INSTRUCTOR,LEARNER')
    # Institution admin
    routes.append('/inst_admin')
    UIOption.objects.create(route='/inst_admin', enabled=True, roles='ADMIN')

    # Invalidate the cache
    from tesla_ce.models.ui_option import get_role_base_ui_routes
    get_role_base_ui_routes.invalidate()

    yield routes
