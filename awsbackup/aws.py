# -*- coding: utf-8 -*-


import urllib.error
import urllib.parse
import urllib.request

import boto3
import botocore
from decouple import config


class AWSSession:
    """
    Class to interact wit Amazon Web Service (AWS) API through boto3 library
    """
    GPS_BUCKET_NAME = config('GPS_BUCKET_NAME')
    OP_PROGRAM_BUCKET_NAME = config('OP_PROGRAM_BUCKET_NAME')
    TRIP_BUCKET_NAME = config('TRIP_BUCKET_NAME')
    REPRESENTATIVE_WEEk_BUCKET_NAME = config('REPRESENTATIVE_WEEk_BUCKET_NAME')
    FILE_196_BUCKET_NAME = config('FILE_196_BUCKET_NAME')
    PROFILE_BUCKET_NAME = config('PROFILE_BUCKET_NAME')
    STAGE_BUCKET_NAME = config('STAGE_BUCKET_NAME')
    SPEED_BUCKET_NAME = config('SPEED_BUCKET_NAME')
    TRANSACTION_BUCKET_NAME = config('TRANSACTION_BUCKET_NAME')
    OP_SPEED_BUCKET_NAME = config('OP_SPEED_BUCKET_NAME')
    STOP_TIMES_BUCKET_NAME = config('STOP_TIMES_BUCKET_NAME')
    EARLY_TRANSACTION_BUCKET_NAME = config('EARLY_TRANSACTION_BUCKET_NAME')
    MISCELLANEOUS_BUCKET_NAME = config('MISCELLANEOUS_BUCKET_NAME')

    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=config('AWS_SECRET_ACCESS_KEY'))

    def retrieve_obj_list(self, bucket_name):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        obj_list = []
        for obj in bucket.objects.all():
            size_in_mb = float(obj.size) / (1024 ** 2)
            url = self._build_url(obj.key, bucket_name)
            obj_list.append(dict(name=obj.key, size=size_in_mb, last_modified=obj.last_modified, url=url))

        return obj_list

    def get_available_days(self, bucket_name):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(bucket_name)

        days = []
        for obj in bucket.objects.all():
            date = obj.key.split('.')[0]
            days.append(date)

        return days

    def check_bucket_exists(self, bucket_name):
        s3 = self.session.resource('s3')
        try:
            s3.meta.client.head_bucket(Bucket=bucket_name)
            return True
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(e.response['Error']['Code'])
            if error_code == 403:
                raise ValueError("Private Bucket. Forbidden Access!")
            elif error_code == 404:
                return False

    def check_file_exists(self, bucket_name, key):
        s3 = self.session.resource('s3')
        try:
            s3.Object(bucket_name, key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                return False
            else:
                raise ValueError(e.response['Error'])
        else:
            return True

    def _build_url(self, key, bucket_name):
        return ''.join(['https://s3.amazonaws.com/', bucket_name, '/', urllib.parse.quote(key)])

    def create_download_link(self, key, bucket_name, expire_time):
        s3 = self.session.client('s3')

        if self.check_bucket_exists(bucket_name) and self.check_file_exists(bucket_name, key):
            url = s3.generate_presigned_url(ClientMethod='get_object', Params={'Bucket': bucket_name, 'Key': key},
                                            ExpiresIn=expire_time, )
            return url
        else:
            raise ValueError('it was a problem to create url')

    def send_file_to_bucket(self, file_path, file_key, bucket_name):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        bucket.upload_file(file_path, file_key)

        return self._build_url(file_key, bucket_name)

    def send_object_to_bucket(self, obj, obj_key, bucket_name):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(bucket_name)
        bucket.upload_fileobj(obj, obj_key)
        s3.Object(bucket_name, obj_key).Acl().put(ACL='public-read')

        return self._build_url(obj_key, bucket_name)

    def delete_object_in_bucket(self, obj_key, bucket_name):
        s3 = self.session.resource('s3')
        obj = s3.Object(bucket_name, obj_key)

        return obj.delete()
