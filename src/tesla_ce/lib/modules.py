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
""" TeSLA modules definition module"""


def get_modules():
    """
        Get the description of all modules

        :return: Dictionary with all modules and properties
        :rtype: dict
    """
    return {
        'api': get_api_properties(),
        'lapi': get_lapi_properties(),
        'worker': get_worker_properties(),
        'beat': get_beat_properties(),
        'worker-all': get_worker_all_properties(),
        'worker-enrolment': get_worker_enrol_properties(),
        'worker-enrolment-storage': get_worker_enrol_storage_properties(),
        'worker-enrolment-validation': get_worker_enrol_validation_properties(),
        'worker-verification': get_worker_verification_properties(),
        'worker-alerts': get_worker_alerts_properties(),
        'worker-reporting': get_worker_reporting_properties(),
    }


def get_api_properties():
    """
        Returns the definition of the API module

        :return: Definition of the API module
        :rtype: dict
    """
    return {
        'module': 'api',
        'description': 'TeSLA API',
        'apps': ['tesla_ce.apps.api'],
        'services': {
            'django': ['django/config'],
            'db': ['db/config', 'db/credentials/rw_access'],
            'vault': ['vault/jwt/learners/create', 'vault/jwt/learners/validate',
                      'vault/jwt/instructors/create', 'vault/jwt/instructors/validate',
                      'vault/jwt/module/all/validate', 'vault/jwt/module/all/create',
                      'vault/jwt/users/create', 'vault/jwt/users/validate',
                      'vault/vle/write', 'vault/policy/write', 'vault/provider/write',
                      ],
            'redis': ['redis/config'],
            'storage': ['storage/config'],
            'celery': ['celery/config', 'celery/queues', 'celery/credentials/api'],
        },
        'deployment': {
            'type': 'service',
            'public': True,
            'base_path': 'api',
        },
        'dependencies': [],
    }


def get_lapi_properties():
    """
        Returns the definition of the Learner API module

        :return: Definition of the Learner API module
        :rtype: dict
    """
    return {
        'module': 'lapi',
        'description': 'TeSLA Learner API',
        'apps': ['tesla_ce.apps.lapi'],
        'services': {
            'django': ['django/config'],
            'redis': ['redis/config'],
            'storage': ['storage/config'],
            'vault': ['vault/jwt/learners/validate', 'vault/jwt/users/validate'],
            'celery': ['celery/config', 'celery/queues', 'celery/credentials/lapi'],
        },
        'deployment': {
            'type': 'service',
            'public': True,
            'base_path': 'lapi',
        },
        'dependencies': [],
    }


def get_worker_properties():
    """
        Returns the definition of the Worker module

        :return: Definition of the worker module
        :rtype: dict
    """
    return {
        'module': 'worker',
        'description': 'TeSLA Worker',
        'apps': [],
        'services': {
            'django': ['django/config'],
            'db': ['db/config', 'db/credentials/rw_access'],
            'celery': ['celery/config', 'celery/queues', 'celery/credentials/worker'],
            'redis': ['redis/config'],
            'storage': ['storage/config'],
        },
        'deployment': {
            'type': 'worker',
            'public': False,
            'base_path': None,
            'queues': ['DEFAULT']
        },
        'dependencies': [],
    }


def get_worker_all_properties():
    """
        Returns the definition of the Worker process for all processing tasks

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-all'
    generic_worker['description'] = 'TeSLA Worker performing all process tasks'
    generic_worker['deployment']['queues'] = ['__all__']
    return generic_worker


def get_worker_enrol_properties():
    """
        Returns the definition of the Worker process for generic enrolment tasks

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-enrolment'
    generic_worker['description'] = 'TeSLA Worker performing generic enrolment tasks'
    generic_worker['deployment']['queues'] = ['ENROLMENT']
    return generic_worker


def get_worker_enrol_storage_properties():
    """
        Returns the definition of the Worker process devoted to store enrolment samples

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-enrolment-storage'
    generic_worker['description'] = 'TeSLA Worker performing enrolment storage tasks'
    generic_worker['deployment']['queues'] = ['ENROLMENT_STORAGE']
    return generic_worker


def get_worker_enrol_validation_properties():
    """
        Returns the definition of the Worker process for enrolment samples validation tasks

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-enrolment-validation'
    generic_worker['description'] = 'TeSLA Worker performing enrolment sample validation tasks'
    generic_worker['deployment']['queues'] = ['ENROLMENT_VALIDATION']
    return generic_worker


def get_worker_verification_properties():
    """
        Returns the definition of the Worker process for verification tasks

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-verification'
    generic_worker['description'] = 'TeSLA Worker performing verification tasks'
    generic_worker['deployment']['queues'] = ['VERIFICATION']
    return generic_worker


def get_worker_reporting_properties():
    """
        Returns the definition of the Worker process for reporting tasks

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-reporting'
    generic_worker['description'] = 'TeSLA Worker performing reporting tasks'
    generic_worker['deployment']['queues'] = ['REPORTING']
    return generic_worker


def get_worker_alerts_properties():
    """
        Returns the definition of the Worker process for alerts processing tasks

        :return: Definition of the worker module
        :rtype: dict
    """
    generic_worker = get_worker_properties()
    generic_worker['module'] = 'worker-alerts'
    generic_worker['description'] = 'TeSLA Worker performing alerts processing tasks'
    generic_worker['deployment']['queues'] = ['ALERTS']
    return generic_worker


def get_beat_properties():
    """
        Returns the definition of the Worker Beat module

        :return: Definition of the worker beat module
        :rtype: dict
    """
    return {
        'module': 'beat',
        'description': 'TeSLA Worker Beat',
        'apps': [],
        'services': {
            'django': ['django/config'],
            'db': ['db/config', 'db/credentials/rw_access'],
            'celery': ['celery/config', 'celery/queues', 'celery/credentials/beat'],
        },
        'deployment': {
            'type': 'beat',
            'public': False,
            'base_path': None,
        },
        'dependencies': [],
    }


def get_vle_properties():
    """
        Returns the definition of a VLE module

        :return: Definition of a VLE module
        :rtype: dict
    """
    return {
        'module': 'vle',
        'description': 'TeSLA VLE',
        'apps': [],
        'services': {
        },
        'deployment': {
            'type': None,
            'public': False,
            'base_path': None,
        },
        'dependencies': ['api', 'lapi'],
    }


def get_provider_properties():
    """
        Returns the definition of a Provider module

        :return: Definition of a Provider module
        :rtype: dict
    """
    return {
        'module': 'provider',
        'description': 'TeSLA Provider',
        'apps': [],
        'services': {
            'celery': ['celery/config', 'celery/credentials/provider'],
        },
        'deployment': {
            'type': None,
            'public': False,
            'base_path': None,
        },
        'dependencies': ['api'],
    }
