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
""" Storage Manager Module"""
from botocore import exceptions
from django.core.management import call_command
from ..config import ConfigManager
from ..exception import TeslaStorageException


class StorageManager:
    """ Manager class for Storage """

    #: Storage url
    storage_url: str = None

    #: Storage client
    _client = None

    def __init__(self, config=None):
        """
            Default constructor
            :param config: Configuration manager instance
            :type config: ConfigManager
        """
        if config is None:
            config = ConfigManager()

        # Store the configuration object
        self._config = config

    @property
    def client(self):
        """
            Access to the Storage server
            :return: Storage server object
            :rtype: s3boto3.S3Boto3Storage
        """
        if self._client is None:
            # Import when client is created to avoid errors during installation process
            from storages.backends import s3boto3
            self._client = s3boto3.S3Boto3Storage()
        return self._client

    def initialize(self):
        """
            Initialize the storage
        """
        # Get the list of buckets
        buckets = [b.name for b in self._client.connection.buckets.all()]

        # Create the bucket if it does not exist
        if self._config.config.get('STORAGE_BUCKET_NAME') not in buckets:
            self.create_default_bucket()
        if self._config.config.get('STORAGE_PUBLIC_BUCKET_NAME') not in buckets:
            self.create_public_bucket()

        # Export static files
        call_command('collectstatic', verbosity=0, interactive=False)

    def create_default_bucket(self):
        """
            Create the default bucket in the configuration
        """
        # Get configuration
        bucket = self._config.config.get('STORAGE_BUCKET_NAME')
        region = self._config.config.get('STORAGE_REGION')
        # Create bucket
        try:
            if region is None:
                self._client.connection.create_bucket(Bucket=bucket, ACL='private')
            else:
                self._client.connection.create_bucket(Bucket=bucket, ACL='private',
                                                      CreateBucketConfiguration={'LocationConstraint': region})
        except exceptions.ClientError as e:
            raise TeslaStorageException('Cannot create bucket {} at region {}: {}'.format(bucket, region, str(e)))

    def create_public_bucket(self):
        """
            Create the public bucket in the configuration
        """
        # Get configuration
        bucket = self._config.config.get('STORAGE_PUBLIC_BUCKET_NAME')
        region = self._config.config.get('STORAGE_REGION')
        # Create bucket
        try:
            if region is None:
                self._client.connection.create_bucket(Bucket=bucket, ACL='download')
            else:
                self._client.connection.create_bucket(Bucket=bucket, ACL='download',
                                                      CreateBucketConfiguration={'LocationConstraint': region})
        except exceptions.ClientError as e:
            raise TeslaStorageException('Cannot create bucket {} at region {}: {}'.format(bucket, region, str(e)))

    def get_status(self):
        """
            Get the storage status

            :return: Object with status information
            :rtype: dict
        """
        errors = []
        warnings = []

        can_connect = False
        ready = False
        try:
            self.client.listdir('/')
            can_connect = True
            ready = True
        except exceptions.ClientError as e:
            if e.response['Error']['Code'] == "NoSuchBucket":
                can_connect = True
                warnings.append('Bucket {} does not exist'.format(self.client.bucket_name))
            elif e.response['Error']['Code'] == "InvalidAccessKeyId" or \
                    e.response['Error']['Code'] == "SignatureDoesNotMatch":
                errors.append('Invalid credentials')
            else:
                errors.append('Could not connect to URL {}'.format(self.client.endpoint_url))
        except exceptions.EndpointConnectionError:
            errors.append('Could not connect to URL {}'.format(self.client.endpoint_url))
        except exceptions.SSLError:
            errors.append('Invalid SSL certificate connecting to URL {}'.format(self.client.endpoint_url))
        except Exception as e:
            errors.append('Error connecting to storage server: {}'.format(str(e)))
        status = 1
        if not can_connect:
            status = 0
        return {
            'status': status,
            'warnings': len(warnings),
            'errors': len(errors),
            'info': {
                'ready': ready,
                'errors': errors,
                'warnings': warnings,
            }
        }
