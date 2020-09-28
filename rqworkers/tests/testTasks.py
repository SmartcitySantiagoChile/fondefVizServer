import os
from smtplib import SMTPException

import mock
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from fakeredis import FakeStrictRedis
from rq import Queue

from datamanager.models import UploaderJobExecution, LoadFile, ExporterJobExecution
from rqworkers.tasks import upload_file_job, upload_exception_handler, export_data_job, export_exception_handler, \
    count_line_of_file_job


class TaskTest(TestCase):

    def setUp(self):
        count = 1
        LoadFile.objects.create(id=count, dataSourcePath='/', discoveredAt=timezone.now(), lines=1,
                                lastModified=timezone.now())

        UploaderJobExecution.objects.create(id=1, jobId='d8c961e5-db5b-4033-a27f-6f2d30662548',
                                            enqueueTimestamp=timezone.now(),
                                            executionStart=timezone.now(),
                                            executionEnd=timezone.now(),
                                            status='',
                                            errorMessage='',
                                            file_id=1,
                                            wasDeletedAt=None)

        ExporterJobExecution.objects.create(id=1, jobId='d8c961e5-db5b-4033-a27f-6f2d30662548',
                                            enqueueTimestamp=timezone.now(),
                                            executionStart=timezone.now(),
                                            executionEnd=timezone.now(),
                                            status='',
                                            errorMessage='',
                                            file='file',
                                            query='{"query": {"bool": {"filter": [{"terms": {"operator": [1, 2, 3, 4, 5, 6, 7, 8, 9]}}, {"term": {"route": "T549 00I"}}, {"range": {"expeditionStartTime": {"gte": "2019-10-17||/d", "lte": "2019-10-17||/d", "format": "yyyy-MM-dd", "time_zone": "+00:00"}}}, {"term": {"notValid": 0}}]}}, "_source": ["busCapacity", "licensePlate", "route", "loadProfile", "expeditionDayId", "expandedAlighting", "expandedBoarding", "expeditionStartTime", "expeditionEndTime", "authStopCode", "timePeriodInStartTime", "dayType", "timePeriodInStopTime", "busStation", "path", "notValid"]}',
                                            user_id=1,
                                            seen=True,
                                            fileType='profile',
                                            filters=' Hora_inicio_expedición: entre 2020-10-17 00:00:00 y 2020-10-17 23:59:59<br /> y Código_parada_transantiago: T-20-205-SN-44<br />')

        User.objects.create_user('test_user', id=1)

        self.queue = Queue(is_async=False, connection=FakeStrictRedis())

        self.file_path_list = ["files/2016-03-14.trip", "files/2016-03-14.trip.gz", "files/2016-03-14.trip.zip",
                               "files/2017-04-03.shape"]
        self.file_list = []
        for file_path in self.file_path_list:
            count += 1
            name = file_path.split("/")[1]
            self.file_list.append(LoadFile.objects.get_or_create(id=count, fileName=name, defaults={
                'dataSourcePath': file_path,
                'discoveredAt': timezone.now(),
                'lastModified': timezone.now()
            })[0])

    @mock.patch('rqworkers.tasks.upload_file')
    def test_upload_file_job_correct(self, upload_file):
        job = self.queue.enqueue(upload_file_job, "", [0], job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        job_uploader = UploaderJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(job_uploader.status, 'finished')
        self.assertTrue(job.is_finished)

    @mock.patch('rqworkers.tasks.upload_file')
    @mock.patch('django.db.models.query.QuerySet.get')
    def test_upload_file_job_with_first_error(self, uploader_job_execution, upload_file):
        uploader_job_in_db = UploaderJobExecution.objects.get(jobId='test_id')
        uploader_job_execution.side_effect = [UploaderJobExecution.DoesNotExist, uploader_job_in_db]
        job = self.queue.enqueue(upload_file_job, "", [0], job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertTrue(job.is_finished)

    @mock.patch('rqworkers.tasks.traceback')
    @mock.patch('django.db.models.query.QuerySet.get')
    def test_upload_exception_handler_does_not_exist(self, uploader_job_execution, traceback):
        job_instance = mock.MagicMock(id=1)
        e = UploaderJobExecution.DoesNotExist
        uploader_job_execution.side_effect = e
        self.assertTrue(upload_exception_handler(job_instance, type(e),
                                                 e, e().__traceback__))
        traceback.format_exception.assert_called_once()

    @mock.patch('rqworkers.tasks.traceback')
    def test_upload_exception_handler_correct(self, traceback):
        job_instance = mock.MagicMock(id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        e = UploaderJobExecution.DoesNotExist()
        self.assertTrue(upload_exception_handler(job_instance, type(e), e, e.__traceback__))
        updatedJob = UploaderJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(updatedJob.status, 'failed')
        self.assertEqual(updatedJob.errorMessage, "<class 'datamanager.models.UploaderJobExecution.DoesNotExist'>\n\n")
        traceback.format_exception.assert_called_once()

    @mock.patch('rqworkers.tasks.download_file')
    @mock.patch('rqworkers.tasks.send_mail')
    def test_export_data_job_correct(self, send_mail, download_file):
        job = self.queue.enqueue(export_data_job, "", '', job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        job_uploader = ExporterJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(job_uploader.status, 'finished')
        self.assertTrue(job.is_finished)

    @mock.patch('django.db.models.query.QuerySet.get')
    @mock.patch('rqworkers.tasks.download_file')
    @mock.patch('rqworkers.tasks.send_mail')
    def test_export_data_job_correct_with_first_error(self, send_mail, download_file, exporter_job_execution):
        exporter_job_in_dbb = ExporterJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')

        exporter_job_execution.side_effect = [ExporterJobExecution.DoesNotExist, exporter_job_in_dbb]
        job = self.queue.enqueue(export_data_job, "", '', job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertTrue(job.is_finished)

    @mock.patch('django.db.models.query.QuerySet.get')
    def test_export_data_but_job_id_does_not_exist(self, exporter_job_execution):
        exporter_job_execution.side_effect = [ExporterJobExecution.DoesNotExist, ExporterJobExecution.DoesNotExist]
        job_id = 'd8c961e5-db5b-4033-a27f-6f2d30662548'
        with self.assertRaisesMessage(
                ValueError, 'job id "{0}" does not have a record in ExporterJobExecution model'.format(job_id)):
            self.queue.enqueue(export_data_job, "", '', job_id=job_id)

    @mock.patch('rqworkers.tasks.download_file')
    @mock.patch('rqworkers.tasks.send_mail')
    def test_export_data_job_correct_with_STMP_error(self, send_mail, download_file):
        send_mail.side_effect = SMTPException
        job = self.queue.enqueue(export_data_job, "", '', job_id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        job_uploader = ExporterJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(ExporterJobExecution.FINISHED_BUT_MAIL_WAS_NOT_SENT, job_uploader.status)
        self.assertTrue(job.is_finished)

    @mock.patch('django.db.models.query.QuerySet.get')
    @mock.patch('rqworkers.tasks.traceback')
    def test_export_exception_handler_does_not_exist(self, traceback, export_job_execution):
        job_instance = mock.MagicMock(id=1)
        e = ExporterJobExecution.DoesNotExist
        export_job_execution.side_effect = e
        self.assertTrue(export_exception_handler(job_instance, type(e), e, e().__traceback__))
        traceback.format_exception.assert_called_once()

    @mock.patch('rqworkers.tasks.traceback')
    def test_export_exception_handler_correct(self, traceback):
        job_instance = mock.MagicMock(id='d8c961e5-db5b-4033-a27f-6f2d30662548')
        e = ExporterJobExecution.DoesNotExist
        self.assertTrue(export_exception_handler(job_instance, type(e()), e(), e().__traceback__))
        updatedJob = ExporterJobExecution.objects.get(jobId='d8c961e5-db5b-4033-a27f-6f2d30662548')
        self.assertEqual(updatedJob.status, 'failed')
        self.assertEqual(updatedJob.errorMessage, "<class 'datamanager.models.ExporterJobExecution.DoesNotExist'>\n\n")

    def test_count_line_of_file_job_correct(self):
        job = self.queue.enqueue(count_line_of_file_job, self.file_list[0], 'trip',
                                 os.path.join(os.path.dirname(__file__), self.file_path_list[0]))
        count_line_obj = LoadFile.objects.get(dataSourcePath=self.file_path_list[0])
        self.assertTrue(job.is_finished)
        self.assertEqual(9, count_line_obj.lines)

    def test_count_line_of_file_job_correct_gz(self):
        job = self.queue.enqueue(count_line_of_file_job, self.file_list[1], 'trip',
                                 os.path.join(os.path.dirname(__file__), self.file_path_list[1]))
        count_line_obj = LoadFile.objects.get(dataSourcePath=self.file_path_list[1])
        self.assertTrue(job.is_finished)
        self.assertEqual(9, count_line_obj.lines)

    def test_count_line_of_file_job_correct_zip(self):
        job = self.queue.enqueue(count_line_of_file_job, self.file_list[2], 'trip',
                                 os.path.join(os.path.dirname(__file__), self.file_path_list[2]))
        count_line_obj = LoadFile.objects.get(dataSourcePath=self.file_path_list[2])
        self.assertTrue(job.is_finished)
        self.assertEqual(9, count_line_obj.lines)

    def test_count_line_of_file_job_correct_shape(self):
        job = self.queue.enqueue(count_line_of_file_job, self.file_list[3], 'shape',
                                 os.path.join(os.path.dirname(__file__), self.file_path_list[3]))
        count_line_obj = LoadFile.objects.get(dataSourcePath=self.file_path_list[3])
        self.assertTrue(job.is_finished)
        self.assertEqual(1, count_line_obj.lines)
