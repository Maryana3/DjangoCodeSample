from storages.backends.s3boto3 import S3Boto3Storage

from django.conf import settings


class S3Storage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    default_acl = 'public-read'
