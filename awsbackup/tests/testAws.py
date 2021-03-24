from unittest import TestCase
import awsbackup.aws as aws
from unittest import mock
import datetime
from botocore.exceptions import ClientError


class AwsTest(TestCase):

    @mock.patch('awsbackup.aws.boto3.Session')
    def setUp(self, boto3_session):
        boto3_session.return_value = mock.MagicMock(resource=mock.MagicMock())
        self.aws_session = aws.AWSSession()

    def test_get_available_days(self):
        date = mock.Mock(key='2020-05-08.transaction.gz')
        dates = mock.Mock(return_value=[date])
        bucket = mock.MagicMock(objects=mock.MagicMock(all=dates))
        bucket.Bucket.return_value = bucket
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        expected_date = ['2020-05-08']
        self.assertEqual(expected_date, self.aws_session.get_available_days('bucket_name'))

    def test_check_bucket_exists_true(self):
        bucket = mock.MagicMock(
            meta=mock.MagicMock(client=mock.MagicMock(head_bucket=mock.MagicMock(return_value=True))))
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        self.assertTrue(self.aws_session.check_bucket_exists('bucket_name'))

    def test_check_bucket_exists_404_error(self):
        error = mock.MagicMock()
        error_response = {'Error': {'Code': '404'}}
        error.side_effect = ClientError(error_response=error_response, operation_name='mock error')
        bucket = mock.MagicMock(
            meta=mock.MagicMock(client=mock.MagicMock(head_bucket=error)))
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        self.assertFalse(self.aws_session.check_bucket_exists('bucket_name'))

    def test_check_bucket_exists_403_error(self):
        error = mock.MagicMock()
        error_response = {'Error': {'Code': '403'}}
        error.side_effect = ClientError(error_response=error_response, operation_name='mock error')
        bucket = mock.MagicMock(
            meta=mock.MagicMock(client=mock.MagicMock(head_bucket=error)))
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)

        with self.assertRaises(ValueError):
            self.aws_session.check_bucket_exists('bucket_name')

    def test_check_file_exists(self):
        load = mock.MagicMock()
        load.load.return_value = '2020-05-08.transaction.gz'
        bucket = mock.MagicMock()
        bucket.Object.return_value = load
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        self.assertTrue(self.aws_session.check_file_exists('2020-05-08.transaction.gz', 'key'))

    def test_check_file_exists_404_error(self):
        error = mock.MagicMock()
        error_response = {'Error': {'Code': '404'}}
        error.load.side_effect = ClientError(error_response=error_response, operation_name='mock error')
        bucket = mock.MagicMock()
        bucket.Object.return_value = error
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        self.assertFalse(self.aws_session.check_file_exists('2020-05-08.transaction.gz', 'key'))

    def test_check_file_exists_403_error(self):
        error = mock.MagicMock()
        error_response = {'Error': {'Code': '403'}}
        error.load.side_effect = ClientError(error_response=error_response, operation_name='mock error')
        bucket = mock.MagicMock()
        bucket.Object.return_value = error
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        with self.assertRaises(ValueError):
            self.aws_session.check_file_exists('2020-05-08.transaction.gz', 'key')

    def test__build_url(self):
        url = 'https://s3.amazonaws.com/bucket_name/key'
        self.assertEqual(url, self.aws_session._build_url('key', 'bucket_name'))

    def test_retrieve_obj_list(self):
        date = mock.MagicMock(size=1000, key='key', last_modified='today')
        dates = mock.Mock(return_value=[date])
        bucket = mock.MagicMock(objects=mock.MagicMock(all=dates))
        bucket.Bucket.return_value = bucket
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        self.assertEqual([{
            'name': 'key',
            'size': 0.00095367431640625,
            'last_modified': 'today',
            'url': 'https://s3.amazonaws.com/bucket_name/key'
        }], self.aws_session.retrieve_obj_list('bucket_name'))

    @mock.patch('awsbackup.aws.AWSSession.check_bucket_exists')
    @mock.patch('awsbackup.aws.AWSSession.check_file_exists')
    def test_create_download_link(self, file_exists, bucket_exists):
        file_exists.return_value = True
        bucket_exists.return_value = True
        url = 'url'
        bucket = mock.MagicMock()
        bucket.generate_presigned_url.return_value = url
        self.aws_session.session.client = mock.MagicMock(return_value=bucket)
        self.assertEqual('url', self.aws_session.create_download_link('key', 'bucket_name', 'today'))

    @mock.patch('awsbackup.aws.AWSSession.check_bucket_exists')
    @mock.patch('awsbackup.aws.AWSSession.check_file_exists')
    def test_create_download_link_error(self, file_exists, bucket_exists):
        file_exists.return_value = False
        bucket_exists.return_value = False
        with self.assertRaises(ValueError):
            self.assertEqual('url', self.aws_session.create_download_link('key', 'bucket_name', 'today'))

    @mock.patch('awsbackup.aws.AWSSession._build_url')
    def test_send_file_to_bucket(self, build_url):
        build_url.return_value = 'url'
        self.aws_session.session.resource = mock.MagicMock()
        self.assertEqual('url', self.aws_session.send_file_to_bucket('path', 'key', 'bucket_name'))

    @mock.patch('awsbackup.aws.AWSSession._build_url')
    def test_send_object_to_bucket(self, build_url):
        build_url.return_value = 'url'
        self.aws_session.session.resource = mock.MagicMock()
        self.assertEqual('url', self.aws_session.send_object_to_bucket('obj', 'key', 'bucket_name'))

    def test_delete_object_in_bucket(self):
        bucket = mock.MagicMock()
        bucket.Object.return_value = bucket
        bucket.delete.return_value = 'delete'
        self.aws_session.session.resource = mock.MagicMock(return_value=bucket)
        self.assertEqual('delete', self.aws_session.delete_object_in_bucket('key', 'bucket_name'))
