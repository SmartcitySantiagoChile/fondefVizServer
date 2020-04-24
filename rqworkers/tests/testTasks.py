import mock
from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis
from rq import Queue

from datamanager.models import UploaderJobExecution, LoadFile
from rqworkers.tasks import upload_file_job, upload_exception_handler


class TaskTest(TestCase):

    def setUp(self):
        LoadFile.objects.create(id=1, dataSourcePath='/', discoveredAt=timezone.now(), lines=1,
                                lastModified=timezone.now())

        UploaderJobExecution.objects.create(id=1, jobId='d8c961e5-db5b-4033-a27f-6f2d30662548',
                                            enqueueTimestamp=timezone.now(),
                                            executionStart=timezone.now(),
                                            executionEnd=timezone.now(),
                                            status='',
                                            errorMessage='',
                                            file_id=1,
                                            wasDeletedAt=None)

        self.queue = Queue(is_async=False, connection=FakeStrictRedis())

    @mock.patch('rqworkers.tasks.upload_file')
    def test_upload_file_job_correct(self, upload_file):
        upload_file.return_value = mock.Mock()
        job = self.queue.enqueue(upload_file_job, "", [0], job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        job_uploader = UploaderJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(job_uploader.status, 'finished')
        self.assertTrue(job.is_finished)

    @mock.patch('rqworkers.tasks.upload_file')
    @mock.patch('django.db.models.query.QuerySet.get')
    def test_upload_file_job_with_first_error(self, uploader_job_execution, upload_file):
        uploader_job_in_dbb = UploaderJobExecution.objects.get(jobId='test_id')
        uploader_job_execution.side_effect = [UploaderJobExecution.DoesNotExist, uploader_job_in_dbb]
        upload_file.return_value = mock.Mock()
        job = self.queue.enqueue(upload_file_job, "", [0], job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertTrue(job.is_finished)

    @mock.patch('django.db.models.query.QuerySet.get')
    @mock.patch('rqworkers.tasks.traceback')
    def test_upload_exception_handler_does_not_exist(self, traceback, uploader_job_execution):
        job_instance = mock.MagicMock(id=1)
        traceback.return_value = mock.MagicMock()
        uploader_job_execution.side_effect = UploaderJobExecution.DoesNotExist
        self.assertTrue(upload_exception_handler(job_instance, UploaderJobExecution.DoesNotExist, "", ""))

    @mock.patch('rqworkers.tasks.traceback')
    def test_upload_exception_handler_correct(self, traceback):
        job_instance = mock.MagicMock(id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        traceback.return_value = mock.MagicMock()
        self.assertTrue(upload_exception_handler(job_instance, UploaderJobExecution.DoesNotExist, "", ""))
        updatedJob = UploaderJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(updatedJob.status, 'failed')
        self.assertEqual(updatedJob.errorMessage, "<class 'datamanager.models.UploaderJobExecution.DoesNotExist'>\n\n")

    @mock.patch('rqworkers.tasks.get_current_job')
    def test_export_data_job(self, get_current_job):
        get_current_job.return_value = mock.MagicMock(id=1)
