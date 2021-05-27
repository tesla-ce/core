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
""" Policies description module """


def get_service_config_map():
    """
        Get the configuration mappings for all roles
        :return: Configuration and credentials for the different services and roles
        :rtype: dict
    """
    return {
        'public': {
            'map': [
                ('TESLA_DOMAIN', 'config/tesla/domain'),
            ],
            'policy': 'public'
        },
        'db': {
            'config': {
                'map': [
                    ('DB_HOST', 'config/db/host'),
                    ('DB_PORT', 'config/db/port'),
                    ('DB_ENGINE', 'config/db/engine'),
                    ('DB_NAME', 'config/db/name'),
                ],
                'policy': 'db_config'
            },
            'credentials': {
                'admin': {
                    'map': [
                        ('DB_USER', 'config/db/root_user'),
                        ('DB_PASSWORD', 'config/db/root_password'),
                    ],
                    'policy': 'db_credentials_admin',
                },
                'rw_access': {
                    'map': [
                        ('DB_USER', 'config/db/user'),
                        ('DB_PASSWORD', 'config/db/password'),
                    ],
                    'policy': 'db_credentials_rw_access',
                }
            }
        },
        'vault': {
            'vle': {
                'write': {
                    'map': [],
                    'policy': 'vault_vle_write'
                }
            },
            'provider': {
                'write': {
                    'map': [],
                    'policy': 'vault_provider_write'
                }
            },
            'policy': {
                'write': {
                    'map': [],
                    'policy': 'vault_policy_write'
                }
            },
            'jwt': {
                'default': {
                    'create': {
                        'map': [],
                        'policy': 'vault_jwt_default_create'
                    },
                    'validate': {
                        'map': [],
                        'policy': 'vault_jwt_default_validate'
                    }
                },
                'users': {
                    'create': {
                        'map': [],
                        'policy': 'vault_jwt_users_create'
                    },
                    'validate': {
                        'map': [],
                        'policy': 'vault_jwt_users_validate'
                    }
                },
                'learners': {
                    'create': {
                        'map': [],
                        'policy': 'vault_jwt_learners_create'
                    },
                    'validate': {
                        'map': [],
                        'policy': 'vault_jwt_learners_validate'
                    }
                },
                'instructors': {
                    'create': {
                        'map': [],
                        'policy': 'vault_jwt_instructors_create'
                    },
                    'validate': {
                        'map': [],
                        'policy': 'vault_jwt_instructors_validate'
                    }
                },
                'modules': {
                    'create': {
                        'map': [],
                        'policy': 'vault_jwt_modules_create'
                    },
                    'validate': {
                        'map': [],
                        'policy': 'vault_jwt_modules_validate'
                    }
                },
                'module': {
                    'all': {
                        'validate': {
                            'map': [],
                            'policy': 'vault_jwt_module_all_validate'
                        },
                        'create': {
                            'map': [],
                            'policy': 'vault_jwt_module_all_create'
                        }
                    }
                }
            }
        },
        'django': {
            'config': {
                'map': [
                    ('DJANGO_SECRET_KEY', 'config/django/secret_key'),
                    ('DJANGO_ALLOWED_HOSTS', 'config/django/allowed_hosts'),
                ],
                'policy': 'django_config'
            }
        },
        'redis': {
            'config': {
                'map': [
                    ('REDIS_HOST', 'config/redis/host'),
                    ('REDIS_PORT', 'config/redis/port'),
                    ('REDIS_PASSWORD', 'config/redis/password'),
                    ('REDIS_DATABASE', 'config/redis/database'),
                ],
                'policy': 'redis_config'
            }
        },
        'storage': {
            'config': {
                'map': [
                    ('STORAGE_URL', 'config/storage/url'),
                    ('STORAGE_BUCKET_NAME', 'config/storage/bucket_name'),
                    ('STORAGE_REGION', 'config/storage/region'),
                    ('STORAGE_ACCESS_KEY', 'config/storage/access_key'),
                    ('STORAGE_SECRET_KEY', 'config/storage/secret_key'),
                ],
                'policy': 'storage_config'
            }
        },
        'rabbitmq': {
            'config': {
                'map': [
                    ('RABBITMQ_ADMIN_USER', 'config/rabbitmq/admin_user'),
                    ('RABBITMQ_ADMIN_PASSWORD', 'config/rabbitmq/admin_password'),
                    ('RABBITMQ_ERLANG_COOKIE', 'config/rabbitmq/erlang_cookie'),
                    ('RABBITMQ_PORT', 'config/rabbitmq/port'),
                    ('RABBITMQ_ADMIN_PORT', 'config/rabbitmq/admin_port'),
                ],
                'policy': 'rabbitmq_config'
            }
        },
        'celery': {
            'config': {
                'map': [
                    ('CELERY_BROKER_PROTOCOL', 'config/celery/broker_protocol'),
                    ('CELERY_BROKER_HOST', 'config/celery/broker_host'),
                    ('CELERY_BROKER_PORT', 'config/celery/broker_port'),
                    ('CELERY_BROKER_REGION', 'config/celery/broker_region'),
                    ('CELERY_BROKER_VHOST', 'config/celery/broker_vhost'),
                ],
                'policy': 'celery_config'
            },
            'queues': {
                'map': [
                    ('CELERY_QUEUE_DEFAULT', 'config/celery/queue_default'),
                    ('CELERY_QUEUE_ENROLMENT_STORAGE', 'config/celery/queue_enrolment_storage'),
                    ('CELERY_QUEUE_ENROLMENT_VALIDATION', 'config/celery/queue_enrolment_validation'),
                    ('CELERY_QUEUE_ENROLMENT', 'config/celery/queue_enrolment'),
                    ('CELERY_QUEUE_VERIFICATION', 'config/celery/queue_verification'),
                    ('CELERY_QUEUE_ALERTS', 'config/celery/queue_alerts'),
                    ('CELERY_QUEUE_REPORTING', 'config/celery/queue_reporting'),
                ],
                'policy': 'celery_queues'
            },
            'credentials': {
                'api': {
                    'map': [
                        ('CELERY_BROKER_USER', 'config/celery/credentials/api_user'),
                        ('CELERY_BROKER_PASSWORD', 'config/celery/credentials/api_password'),
                    ],
                    'policy': 'celery_credentials_api',
                },
                'lapi': {
                    'map': [
                        ('CELERY_BROKER_USER', 'config/celery/credentials/lapi_user'),
                        ('CELERY_BROKER_PASSWORD', 'config/celery/credentials/lapi_password'),
                    ],
                    'policy': 'celery_credentials_lapi',
                },
                'worker': {
                    'map': [
                        ('CELERY_BROKER_USER', 'config/celery/credentials/worker_user'),
                        ('CELERY_BROKER_PASSWORD', 'config/celery/credentials/worker_password'),
                    ],
                    'policy': 'celery_credentials_worker',
                },
                'beat': {
                    'map': [
                        ('CELERY_BROKER_USER', 'config/celery/credentials/beat_user'),
                        ('CELERY_BROKER_PASSWORD', 'config/celery/credentials/beat_password'),
                    ],
                    'policy': 'celery_credentials_beat',
                },
                'provider': {
                    'map': [
                        ('CELERY_BROKER_USER', 'config/celery/credentials/provider_user'),
                        ('CELERY_BROKER_PASSWORD', 'config/celery/credentials/provider_password'),
                    ],
                    'policy': 'celery_credentials_provider',
                },
            }
        }
    }


def get_policies():
    """
        Get the policy definitions
        :return: Policy definition for each defined policy
        :rtype: dict
    """
    return {
        'public': {
            'path': {
                '<kv_path>/data/config/public/*': {
                    'capabilities': ['read', 'list']
                },
                '<kv_path>/data/config/tesla/domain': {
                    'capabilities': ['read', 'list']
                }
            }
        },
        'vault_vle_write': {
            "path": {
                "<kv_path>/data/modules/vle_*": {
                    "capabilities": ["read", "list", "create", "update", "delete"]
                },
                "auth/<approle_path>/role/vle_*": {
                    "capabilities": ["read", "list", "create", "update", "delete", "sudo"]
                },
                '<transit_path>/keys/jwt_module_vle_*': {
                    "capabilities": ["read", "list", "create", "update", "delete", "sudo"]
                },
            }
        },
        'vault_provider_write': {
            "path": {
                "<kv_path>/data/modules/provider_*": {
                    "capabilities": ["read", "list", "create", "update", "delete"]
                },
                "<kv_path>/data/config/celery/credentials/provider_*": {
                    "capabilities": ["read", "list", "create", "update", "delete"]
                },
                "auth/<approle_path>/role/provider_*": {
                    "capabilities": ["read", "list", "create", "update", "delete", "sudo"]
                },
                '<transit_path>/keys/jwt_module_provider_*': {
                    "capabilities": ["read", "list", "create", "update", "delete", "sudo"]
                },
            }
        },
        'vault_jwt_default_create': {
            'path': {
                '<transit_path>/sign/jwt_default': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/sign/jwt_default/*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/keys/jwt_default': {
                    'capabilities': ['read']
                },
            }
        },
        'vault_jwt_default_validate': {
            'path': {
                '<transit_path>/verify/jwt_default': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/verify/jwt_default/*': {
                    'capabilities': ['create', 'update']
                }
            }
        },
        'vault_jwt_users_create': {
            'path': {
                '<transit_path>/sign/jwt_users': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/sign/jwt_users/*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/keys/jwt_users': {
                    'capabilities': ['read']
                },
            }
        },
        'vault_jwt_users_validate': {
            'path': {
                '<transit_path>/verify/jwt_users': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/verify/jwt_users/*': {
                    'capabilities': ['create', 'update']
                }
            }
        },
        'vault_jwt_instructors_create': {
            'path': {
                '<transit_path>/sign/jwt_instructors': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/sign/jwt_instructors/*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/keys/jwt_instructors': {
                    'capabilities': ['read']
                },
            }
        },
        'vault_jwt_instructors_validate': {
            'path': {
                '<transit_path>/verify/jwt_instructors': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/verify/jwt_instructors/*': {
                    'capabilities': ['create', 'update']
                }
            }
        },
        'vault_jwt_learners_create': {
            'path': {
                '<transit_path>/sign/jwt_learners': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/sign/jwt_learners/*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/keys/jwt_learners': {
                    'capabilities': ['read']
                },
            }
        },
        'vault_jwt_learners_validate': {
            'path': {
                '<transit_path>/verify/jwt_learners': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/verify/jwt_learners/*': {
                    'capabilities': ['create', 'update']
                }
            }
        },
        'vault_jwt_module_all_validate': {
            'path': {
                '<transit_path>/verify/jwt_module_*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/verify/jwt_module_*/*': {
                    'capabilities': ['create', 'update']
                }
            }
        },
        'vault_jwt_module_all_create': {
            'path': {
                '<transit_path>/sign/jwt_module_*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/sign/jwt_module_*/*': {
                    'capabilities': ['create', 'update']
                },
                '<transit_path>/keys/jwt_module_*': {
                    'capabilities': ['read']
                },
            }
        },
        'vault_policy_write': {
            'path': {
                'sys/policy/<policy_prefix>modules_vle_*': {
                    'capabilities': ['create', 'update', 'read', 'delete', 'list', 'sudo']
                },
                'sys/policy/<policy_prefix>modules_provider_*': {
                    'capabilities': ['create', 'update', 'read', 'delete', 'list', 'sudo']
                },
            }
        },
        'db_config': {
            'path': {
                '<kv_path>/data/config/db/host': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/db/port': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/db/engine': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/db/name': {
                    'capabilities': ['read']
                },
            }
        },
        'db_credentials_admin': {
            'path': {
                '<kv_path>/data/config/db/root_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/db/root_password': {
                    'capabilities': ['read']
                },
            }
        },
        'db_credentials_rw_access': {
            'path': {
                '<kv_path>/data/config/db/user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/db/password': {
                    'capabilities': ['read']
                },
            }
        },
        'django_config': {
            'path': {
                '<kv_path>/data/config/django/*': {
                    'capabilities': ['read']
                }
            }
        },
        'redis_config': {
            'path': {
                '<kv_path>/data/config/redis/host': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/redis/port': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/redis/database': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/redis/password': {
                    'capabilities': ['read']
                },
            }
        },
        'storage_config': {
            'path': {
                '<kv_path>/data/config/storage/url': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/storage/bucket_name': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/storage/region': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/storage/access_key': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/storage/secret_key': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_config': {
            'path': {
                '<kv_path>/data/config/celery/broker_protocol': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/broker_host': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/broker_port': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/broker_region': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/broker_vhost': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_queues': {
            'path': {
                '<kv_path>/data/config/celery/queue_default': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/queue_enrolment': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/queue_enrolment_storage': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/queue_enrolment_validation': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/queue_verification': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/queue_alerts': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/queue_reporting': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_credentials_api': {
            'path': {
                '<kv_path>/data/config/celery/credentials/api_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/credentials/api_password': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_credentials_lapi': {
            'path': {
                '<kv_path>/data/config/celery/credentials/lapi_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/credentials/lapi_password': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_credentials_worker': {
            'path': {
                '<kv_path>/data/config/celery/credentials/worker_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/credentials/worker_password': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_credentials_beat': {
            'path': {
                '<kv_path>/data/config/celery/credentials/beat_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/credentials/beat_password': {
                    'capabilities': ['read']
                },
            }
        },
        'celery_credentials_provider': {
            'path': {
                '<kv_path>/data/config/celery/credentials/provider_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/celery/credentials/provider_password': {
                    'capabilities': ['read']
                },
            }
        },
        'rabbitmq_config': {
            'path': {
                '<kv_path>/data/config/rabbitmq/admin_user': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/rabbitmq/admin_password': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/rabbitmq/admin_port': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/rabbitmq/port': {
                    'capabilities': ['read']
                },
                '<kv_path>/data/config/rabbitmq/host': {
                    'capabilities': ['read']
                },
            }
        },
    }
