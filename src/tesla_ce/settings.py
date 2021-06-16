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
""" DJango settings module """
import os

from configurations import Configuration

from tesla_ce.lib import ConfigManager
from tesla_ce.lib import VaultManager
from tesla_ce.lib.checks import check_vault_connection
from tesla_ce.lib.exception import TeslaConfigException

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tesla_ce.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Production')


class BaseConfiguration(Configuration):
    """ Base configuration transversal to all options """
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Allowed hosts to access DJango application
    ALLOWED_HOSTS = []

    # Disable Prometheus migrations
    PROMETHEUS_EXPORT_MIGRATIONS = False

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # Celery results
        'django_celery_results',
        'django_celery_beat',
        # Include DJango rest framework
        'rest_framework',
        'django_filters',
        # CORS framework
        'corsheaders',
        # API documentation
        'drf_yasg',
        # Prometheus metrics exporter
        'django_prometheus',
        # Include TeSLA CE app
        'tesla_ce',
    ]

    MIDDLEWARE = [
        'django_prometheus.middleware.PrometheusBeforeMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'corsheaders.middleware.CorsPostCsrfMiddleware',
        #'tesla_ce.lib.auth.tesla_token_auth_middleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'tesla_ce.error.TeslaErrorHandlerMiddleware',
        'django_prometheus.middleware.PrometheusAfterMiddleware',
    ]

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'tesla_ce.wsgi.application'
    ROOT_URLCONF = 'tesla_ce.urls'

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.2/howto/static-files/
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
    STATIC_URL = '/static/'

    # Internationalization
    # https://docs.djangoproject.com/en/2.2/topics/i18n/
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # If your Django app is behind a proxy that sets a header to specify secure
    # connections, AND that proxy ensures that user-submitted headers with the
    # same name are ignored (so that people can't spoof it), set this value to
    # a tuple of (header_name, header_value). For any requests that come in with
    # that header/value, request.is_secure() will return True.
    # WARNING! Only set this if you fully understand what you're doing. Otherwise,
    # you may be opening yourself up to a security risk.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Celery configuration
    CELERY_RESULT_BACKEND = 'django-db'
    CELERY_CACHE_BACKEND = 'django-cache'
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseDatabaseScheduler'

    # Enabled TeSLA modules
    TESLA_MODULES = []

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            #'rest_framework_simplejwt.authentication.JWTTokenUserAuthentication',
            'tesla_ce.lib.auth.JWTAuthentication',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
            'rest_framework_datatables.renderers.DatatablesRenderer',
        ),
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
        'DEFAULT_VERSION': 'v2',
        'ALLOWED_VERSIONS': ['v1', 'v2'],
        #'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
        #'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
        'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesLimitOffsetPagination',
        'PAGE_SIZE': 10
    }

    # TeSLA Authentication configuration
    TESLA_JWT_TOKEN = 'JWT'
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = False

    # todo: review this headers when V1 is deprecated
    CORS_ALLOW_HEADERS = (
        'vleid',
        'VLEID',
        'Authorization',
        'Content-Type'
    )


class Production(BaseConfiguration):
    """
        Production configuration class.
    """
    #: TeSLA configuration
    TESLA_CONFIG = ConfigManager()

    @classmethod
    def _add_storage(cls):
        # Your Amazon Web Services access key, as a string.
        cls.AWS_ACCESS_KEY_ID = cls.TESLA_CONFIG.config.get('STORAGE_ACCESS_KEY')
        # Your Amazon Web Services secret access key, as a string.
        cls.AWS_SECRET_ACCESS_KEY = cls.TESLA_CONFIG.config.get('STORAGE_SECRET_KEY')
        # Your Amazon Web Services storage bucket name, as a string.
        cls.AWS_STORAGE_BUCKET_NAME = cls.TESLA_CONFIG.config.get('STORAGE_BUCKET_NAME')
        # (optional, None or canned ACL, default public-read) Must be either None or from the list of canned ACLs.
        # If set to None then all files will inherit the bucket’s ACL.
        cls.AWS_DEFAULT_ACL = 'private'
        # (optional: default is None) Name of the AWS S3 region to use (eg. eu-west-1)
        cls.AWS_S3_REGION_NAME = cls.TESLA_CONFIG.config.get('STORAGE_REGION')

        # Custom S3 URL to use when connecting to S3, including scheme. Overrides AWS_S3_REGION_NAME and AWS_S3_USE_SSL.
        cls.AWS_S3_ENDPOINT_URL = cls.TESLA_CONFIG.config.get('STORAGE_URL')

        # Disable SSL verification
        if cls.TESLA_CONFIG.config.get('STORAGE_SSL_VERIFY') is False:
            cls.AWS_S3_VERIFY = False

        # Get the public bucket name
        cls.AWS_S3_STORAGE_PUBLIC_BUCKET_NAME = cls.TESLA_CONFIG.config.get('STORAGE_PUBLIC_BUCKET_NAME')

        if cls.AWS_ACCESS_KEY_ID is not None and cls.AWS_SECRET_ACCESS_KEY is not None:
            cls.DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
            cls.STATICFILES_STORAGE = 'tesla_ce.lib.storage.bucket.PublicS3Boto3Storage'
            cls.STATIC_ROOT = '/'
        else:
            cls.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    @classmethod
    def pre_setup(cls):
        # Load DJango default configuration
        super().pre_setup()

        if len(cls.TESLA_CONFIG.modules) > 0:
            # Starting in production mode
            cls.TESLA_CONFIG.config.set('TESLA_MODE', 'production')

            # Enable modules
            cls.TESLA_MODULES = []
            for module in cls.TESLA_CONFIG.modules:
                cls.TESLA_MODULES.append(module)
                apps = cls.TESLA_CONFIG.modules[module].get('apps', [])
                for app in apps:
                    if app not in cls.INSTALLED_APPS:
                        cls.INSTALLED_APPS.append(app)
                cls.TESLA_CONFIG.config.set('CELERY_QUEUES', cls.TESLA_CONFIG.modules[module].get('queues'))

            # Apply configuration
            cls.SECRET_KEY = cls.TESLA_CONFIG.config.get('DJANGO_SECRET_KEY')
            cls.ALLOWED_HOSTS = cls.TESLA_CONFIG.config.get('DJANGO_ALLOWED_HOSTS')
            cls.DATABASES = cls.TESLA_CONFIG.get_database_config()
            cls.CACHES = cls.TESLA_CONFIG.get_cache_config()
            cls._add_storage()
            cls.CELERY_BROKER_URL = cls.TESLA_CONFIG.get_celery_config()
        else:
            # Starting in configuration mode
            cls.TESLA_CONFIG.config.set('TESLA_MODE', 'config')
            cls.TESLA_CONFIG.config.set('VAULT_MANAGEMENT', True)
            cls.SECRET_KEY = "Configuration Key"
            cls.DATABASES = {
                'default': {
                    #'ENGINE': 'django.db.backends.{}'.format(cls.TESLA_CONFIG.config.get('DB_ENGINE')),
                    'ENGINE': 'django_prometheus.db.backends.{}'.format(cls.TESLA_CONFIG.config.get('DB_ENGINE')),
                    'HOST': cls.TESLA_CONFIG.config.get('DB_HOST'),
                    'NAME': cls.TESLA_CONFIG.config.get('DB_NAME'),
                    'USER': cls.TESLA_CONFIG.config.get('DB_USER'),
                    'PASSWORD': cls.TESLA_CONFIG.config.get('DB_PASSWORD'),
                    'PORT': cls.TESLA_CONFIG.config.get('DB_PORT'),
                },
                'admin': {
                    #'ENGINE': 'django.db.backends.{}'.format(cls.TESLA_CONFIG.config.get('DB_ENGINE')),
                    'ENGINE': 'django_prometheus.db.backends.{}'.format(cls.TESLA_CONFIG.config.get('DB_ENGINE')),
                    'HOST': cls.TESLA_CONFIG.config.get('DB_HOST'),
                    'NAME': cls.TESLA_CONFIG.config.get('DB_NAME'),
                    'USER': cls.TESLA_CONFIG.config.get('DB_ROOT_USER'),
                    'PASSWORD': cls.TESLA_CONFIG.config.get('DB_ROOT_PASSWORD'),
                    'PORT': cls.TESLA_CONFIG.config.get('DB_PORT'),
                }
            }
            cls.CACHES = cls.TESLA_CONFIG.get_cache_config()
            cls._add_storage()
            cls.CELERY_BROKER_URL = cls.TESLA_CONFIG.get_celery_config()

        # Add the URLs to the API and DASHBOARD
        cls.API_URL = 'https://{}'.format(cls.TESLA_CONFIG.config.get('TESLA_DOMAIN'))
        cls.DASHBOARD_URL = 'https://{}'.format(cls.TESLA_CONFIG.config.get('TESLA_DOMAIN'))

        # If no database is selected, remove celery results backend and change to scope auth middleware
        if len(cls.DATABASES) == 0:
            cls.CELERY_RESULT_BACKEND = None

        # Use debug API authentication.
        cls.DEBUG_AUTHENTICATION = False

        # Use debug API authentication object.
        # Can be a pair <type,id> to set desired authentication object
        # Or None for unauthenticated access
        cls.DEBUG_AUTHENTICATION_OBJECT = None


class Dev(Production):
    """
        Development configuration.
    """
    @classmethod
    def pre_setup(cls):
        # Check if Vault is available
        vault_connection_report = check_vault_connection(config=cls.TESLA_CONFIG.config)

        if os.getenv('SSLSERVER') in ['True', 'true', 1, '1']:
            cls.INSTALLED_APPS.append('sslserver')

        # If vault is enabled, apply development actions
        if vault_connection_report['connected']:
            # Unseal Vault if it is sealed
            if vault_connection_report['initialized'] and vault_connection_report['sealed']:
                keys = cls.TESLA_CONFIG.config.get('VAULT_KEYS')
                if keys is not None:
                    cls.TESLA_CONFIG.config.set('VAULT_MANAGEMENT', True)
                    manager = VaultManager(config=cls.TESLA_CONFIG)
                    manager.unseal()
                    # Update vault status
                    vault_connection_report = check_vault_connection(config=cls.TESLA_CONFIG.config)
            # Allow to start as any module
            force_module = os.getenv('TESLA_RUN_AS_MODULE', None)
            if force_module is not None:
                token = cls.TESLA_CONFIG.config.get('VAULT_TOKEN')

                # Check that Vault is ready and token is provided
                if not vault_connection_report['ready']:
                    raise TeslaConfigException('Requested to start as module {}, but Vault is not ready'.format(
                        force_module))
                if token is None:
                    raise TeslaConfigException('Requested to start as module {}, but Vault token is missing'.format(
                        force_module))
                cls.TESLA_CONFIG.config.set('VAULT_MANAGEMENT', True)
                manager = VaultManager(config=cls.TESLA_CONFIG)
                modules = force_module.split(',')
                role_id = []
                secret_id = []
                for module in modules:
                    creds = manager.get_module_credentials(module)
                    role_id.append(creds['role_id'])
                    secret_id.append(creds['secret_id'])
                cls.TESLA_CONFIG.load_vault(role_id=role_id, secret_id=secret_id)

        # Load Production configuration
        super().pre_setup()

        if os.getenv('API_URL') is not None:
            cls.API_URL = os.getenv('API_URL')
        if os.getenv('DASHBOARD_URL') is not None:
            cls.DASHBOARD_URL = os.getenv('DASHBOARD_URL')

        # Enable Debug
        cls.DEBUG = True

        # Enable all hosts
        cls.ALLOWED_HOSTS = ['*']

        # Use debug API authentication.
        cls.DEBUG_AUTHENTICATION = os.getenv('DEBUG_AUTHENTICATION', False) in [1, "1", True, "True", "true"]

        if cls.DEBUG_AUTHENTICATION:
            cls.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = ('tesla_ce.lib.auth.DebugJWTAuthentication',)

        # Use debug API authentication object.
        # Can be a pair <type,id> to set desired authentication object. Type must be: admin, user, vle, provider
        # Or None for unauthenticated access
        cls.DEBUG_AUTHENTICATION_OBJECT = os.getenv('DEBUG_AUTHENTICATION_OBJECT', None)
        if cls.DEBUG_AUTHENTICATION_OBJECT is not None:
            cls.DEBUG_AUTHENTICATION_OBJECT = cls.DEBUG_AUTHENTICATION_OBJECT.replace(" ", "").split(",")
            if cls.DEBUG_AUTHENTICATION_OBJECT[0] not in ["admin", "user", "vle", "provider"]:
                raise Exception(
                    "Invalid authentication object {}. Allowed values are: admin, user, vle, provider".format(
                        cls.DEBUG_AUTHENTICATION_OBJECT[0]
                    )
                )


class Test(Production):
    """
        Test configuration.
    """
    @classmethod
    def pre_setup(cls):
        # Load Production configuration
        super().pre_setup()

        if 'tesla_ce.apps.api' not in cls.INSTALLED_APPS:
            cls.INSTALLED_APPS += ['tesla_ce.apps.api']
        if 'tesla_ce.apps.lapi' not in cls.INSTALLED_APPS:
            cls.INSTALLED_APPS += ['tesla_ce.apps.lapi']

        if 'api' not in cls.TESLA_MODULES:
            cls.TESLA_MODULES += ['api']
        if 'lapi' not in cls.TESLA_MODULES:
            cls.TESLA_MODULES += ['lapi']
