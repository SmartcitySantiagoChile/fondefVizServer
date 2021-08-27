import glob
import os
import re
import sys

from django.core.management.base import BaseCommand
from django.utils import timezone

from datamanager.models import DataSourcePath, LoadFile
from rqworkers.tasks import count_line_of_file_job


class Command(BaseCommand):
    help = 'Search new files and added to file table'

    def add_arguments(self, parser):
        parser.add_argument('--pattern', default=None, help='it process all files that match with pattern')

    def handle(self, *args, **options):
        pattern = options['pattern']

        compiled_pattern = None
        if pattern is not None:
            compiled_pattern = re.compile(pattern)

        for data_source_obj in DataSourcePath.objects.all():
            path = data_source_obj.path

            path_name = os.path.join(path, data_source_obj.filePattern)
            zipped_path_name = os.path.join(path, '{0}.zip'.format(data_source_obj.filePattern))
            gzipped_path_name = os.path.join(path, '{0}.gz'.format(data_source_obj.filePattern))

            def clean_list(l, index):
                return list(map(lambda x: x.split("/")[-1:][0], l))

            path_name_list = glob.glob(path_name)
            clean_name_list = clean_list(path_name_list, -2)
            zipped_name_list = glob.glob(zipped_path_name)
            clean_zipped_name_list = clean_list(zipped_name_list, -3)
            gzipped_name_list = glob.glob(gzipped_path_name)
            clean_gzipped_name_list = clean_list(gzipped_name_list, -3)
            file_name_list = path_name_list + zipped_name_list + gzipped_name_list
            files_name = list(map(lambda x: x.fileName, LoadFile.objects.all()))

            for name in clean_name_list:
                for file in files_name:
                    if name in file:
                        if name != file:
                            print("WARNING:", name, "exist in elasticsearch as", file)
                            sys.exit()

            for name in clean_gzipped_name_list:
                for file in files_name:
                    name_without_gz = "".join(name.split("gz")[:-1])[:-1]
                    if name_without_gz in file:
                        if name != file:
                            print("WARNING:", name, "exist in elasticsearch as", file)
                            sys.exit()

            for name in clean_zipped_name_list:
                for file in files_name:
                    name_without_zip = "".join(name.split("zip")[:-1])[:-1]
                    if name_without_zip in file:
                        if name != file:
                            print("WARNING:", name, "exist in elasticsearch as", file)
                            sys.exit()

            for file_path in file_name_list:
                file_name = os.path.basename(file_path)
                last_modified = timezone.make_aware(timezone.datetime.fromtimestamp(os.path.getmtime(file_path)))
                file_obj, created = LoadFile.objects.get_or_create(fileName=file_name, defaults={
                    'dataSourcePath': path,
                    'discoveredAt': timezone.now(),
                    'lastModified': last_modified
                })
                if created or last_modified != file_obj.lastModified or (
                        pattern is not None and compiled_pattern.search(file_name)):
                    count_line_of_file_job.delay(file_obj, data_source_obj.indexName, file_path)
                    file_obj.lastModified = last_modified
                    if created:
                        self.stdout.write(self.style.SUCCESS('File {0} created successfully'.format(file_name)))
                    else:
                        self.stdout.write(self.style.SUCCESS('File {0} updated successfully'.format(file_name)))
                file_obj.dataSourcePath = path
                file_obj.save()
