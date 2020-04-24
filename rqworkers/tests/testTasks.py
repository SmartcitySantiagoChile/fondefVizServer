import mock
from django.test import TestCase

from datamanager.models import UploaderJobExecution
from rqworkers.tasks import upload_file_job, upload_exception_handler


class TaskTest(TestCase):

    @mock.patch('rqworkers.tasks.upload_file')
    @mock.patch('django.db.models.query.QuerySet.get')
    @mock.patch('rqworkers.tasks.get_current_job')
    def test_upload_file_job(self, get_current_job, uploader_job_execution, upload_file):
        get_current_job.return_value = mock.MagicMock(id=1)
        uploader_job_execution.side_effect = [UploaderJobExecution.DoesNotExist, mock.MagicMock()]
        upload_file.return_value = mock.Mock()
        upload_file_job("", [0])

    @mock.patch('django.db.models.query.QuerySet.get')
    @mock.patch('rqworkers.tasks.traceback')
    def test_upload_exception_handler(self, traceback, uploader_job_execution):
        job_instance = mock.MagicMock(id=1)
        traceback.return_value = mock.MagicMock()
        uploader_job_execution.side_effect = UploaderJobExecution.DoesNotExist
        # DoesNotExist case
        self.assertTrue(upload_exception_handler(job_instance, UploaderJobExecution.DoesNotExist, "", ""))
        uploader_job_execution.side_effect = mock.MagicMock()
        self.assertTrue(upload_exception_handler(job_instance, UploaderJobExecution.DoesNotExist, "", ""))
