# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urllib

import boto3
import botocore
from decouple import config


class AWSSession:
    """
    Class to interact wit Amazon Web Service (AWS) API through boto3 library
    """
    GPS_BUCKET_NAME = 'adatrap-gps'
    OP_PROGRAM_BUCKET_NAME = 'adatrap-opprogram'
    TRIP_BUCKET_NAME = 'adatrap-trip'

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

    def check_file_exists(self, bucket_name, key):
        s3 = self.session.resource('s3')
        try:
            s3.Object(bucket_name, key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                return False
            else:
                # Something else has gone wrong.
                raise ValueError(e.response['Error'])
        else:
            # The object exists.
            return True

    def _build_url(self, key, bucket_name):
        return ''.join(['https://s3.amazonaws.com/', bucket_name, '/', urllib.quote(key)])

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