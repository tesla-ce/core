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
""" Public Bucket definition module """
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class PublicS3Boto3Storage(S3Boto3Storage):
    """
        Storage Bucket for public data (static files)
    """
    bucket_acl = 'download'
    default_acl = 'download'
    bucket_name = settings.AWS_S3_STORAGE_PUBLIC_BUCKET_NAME
    auto_create_bucket = True

    def __init__(self, acl=None, bucket=None, **settings):
        if acl is not None:
            self.bucket_acl = acl
        if bucket is not None:
            self.bucket_name = bucket
        super().__init__(**settings)
