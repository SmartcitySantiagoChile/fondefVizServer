import gzip
import io
import os
import time
import traceback
import uuid
import zipfile
from itertools import groupby
from smtplib import SMTPException

from datauploader.loadData import upload_file
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_rq import job
from rq import get_current_job

from dataDownloader.downloadData import download_file
from datamanager.models import UploaderJobExecution, ExporterJobExecution
from esapi.helper.opdata import ESOPDataHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper


@job('data_uploader')
def upload_file_job(path_to_file, index_name_list):
    job_instance = get_current_job()
    # wait until UploaderJobExecution instance exists
    while True:
        try:
            job_execution_obj = UploaderJobExecution.objects.get(jobId=job_instance.id)
            break
        except UploaderJobExecution.DoesNotExist:
            time.sleep(1)

    job_execution_obj.status = UploaderJobExecution.RUNNING
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.save()

    for index_name in index_name_list:
        upload_file(settings.ES_CLIENT, path_to_file, index_name)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.status = UploaderJobExecution.FINISHED
    job_execution_obj.save()


def upload_exception_handler(job_instance, exc_type, exc_value, exc_tb):
    try:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        job_execution_obj = UploaderJobExecution.objects.get(jobId=job_instance.id)
        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, tb_str)
        job_execution_obj.save()
    except UploaderJobExecution.DoesNotExist:
        pass
    # continue with the next handler if exists, for instance: failed queue
    return True


@job('data_exporter')
def export_data_job(es_query_dict, downloader):
    job_instance = get_current_job()
    job_execution_obj = None
    # wait until ExporterJobExecution instance exists, first time 1 sec , second time 5 seconds, after that raise error
    wait_time_list = [1, 5]
    for wait_time in wait_time_list:
        try:
            job_execution_obj = ExporterJobExecution.objects.get(jobId=job_instance.id)
        except ExporterJobExecution.DoesNotExist:
            time.sleep(wait_time)

    if job_execution_obj is None:
        raise ValueError('job id "{0}" does not have a record in ExporterJobExecution model'.format(job_instance.id))

    job_execution_obj.status = ExporterJobExecution.RUNNING
    job_execution_obj.executionStart = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()

    file_name = "{0}.zip".format(uuid.uuid4())
    zip_file_path = os.path.join(settings.DOWNLOAD_PATH, file_name)
    download_file(settings.ES_CLIENT, es_query_dict, downloader, zip_file_path)

    # update file path
    job_execution_obj.file.name = file_name

    try:
        subject = 'Los datos solicitados ya se encuentran disponibles'
        body = """
        Hola
        
        Los datos que ha solicitado ya están disponibles en la plataforma. Para acceder a ellos siga los siguientes pasos: 
        
        - Ingrese a la plataforma
        - En la sección superior derecha seleccione su nombre de ususario (se desplegará un menú)
        - En el menú presione la opción "Solicitudes de descarga"
        - En este punto encontrará una lista con todas las solicitudes de datos ordenadas por fecha de petición
        
        Recuerde que el archivo estará disponible por 30 días, luego de eso tendrá que volver a generar la consulta.
        
        Saludos
        """
        sender = 'noreply@FondefD10E1002.cl'
        send_mail(subject, body, sender, [job_execution_obj.user.email])

        job_execution_obj.status = ExporterJobExecution.FINISHED
    except SMTPException as e:
        job_execution_obj.status = ExporterJobExecution.FINISHED_BUT_MAIL_WAS_NOT_SENT
        job_execution_obj.errorMessage = str(e)

    job_execution_obj.executionEnd = timezone.now()
    job_execution_obj.seen = False
    job_execution_obj.save()


def export_exception_handler(job_instance, exc_type, exc_value, exc_tb):
    try:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        job_execution_obj = ExporterJobExecution.objects.get(jobId=job_instance.id)

        job_execution_obj.executionEnd = timezone.now()
        job_execution_obj.seen = False
        job_execution_obj.status = UploaderJobExecution.FAILED
        job_execution_obj.errorMessage = '{0}\n{1}\n{2}'.format(exc_type, exc_value, tb_str)
        job_execution_obj.save()
    except ExporterJobExecution.DoesNotExist:
        pass

    # continue with the next handler if exists, for instance: failed queue
    return True


@job('count_lines')
def count_line_of_file_job(file_obj, data_source_code, file_path):
    def is_gzipfile(_file_path):
        with gzip.open(_file_path) as _file_obj:
            try:
                _file_obj.read(1)
                return True
            except OSError:
                return False

    def get_file_object(_file_path):
        """
        :param _file_path: file path will upload
        :return: file object
        """
        if zipfile.is_zipfile(_file_path):
            zip_file_obj = zipfile.ZipFile(_file_path, 'r')
            # it assumes that zip file has only one file
            file_name = zip_file_obj.namelist()[0]
            _file_obj = zip_file_obj.open(file_name, 'r')
        elif is_gzipfile(_file_path):
            _file_obj = gzip.open(_file_path, 'rb')
        else:
            _file_obj = io.open(_file_path, str('rb'))

        return _file_obj

    i = 0
    with get_file_object(file_path) as f:
        if data_source_code in [ESShapeHelper().index_name, ESStopByRouteHelper().index_name,
                                ESOPDataHelper().index_name]:
            if data_source_code in [ESShapeHelper().index_name, ESStopByRouteHelper().index_name]:
                column_id = 0
            elif data_source_code == ESOPDataHelper().index_name:
                column_id = 4
            for group_id, __ in groupby(f, lambda row: row.decode().split(str('|'))[column_id]):
                # lines with hyphen on first column are bad lines and must not be considered
                if group_id != str('-'):
                    i += 1
            # not count header
            i -= 1
        else:
            # how it starts from zero is not count header
            for i, _ in enumerate(f):
                pass
    file_obj.refresh_from_db()
    file_obj.lines = i
    file_obj.save()
