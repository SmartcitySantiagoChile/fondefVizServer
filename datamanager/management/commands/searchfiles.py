# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import os
import re

from django.conf import settings
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
            # TODO: if is running on windows, remove this
            if os.name == 'nt':
                path = os.path.join(settings.BASE_DIR, 'media')

            path_name = os.path.join(path, data_source_obj.filePattern)
            zipped_path_name = os.path.join(path, '{0}.zip'.format(data_source_obj.filePattern))
            gzipped_path_name = os.path.join(path, '{0}.gz'.format(data_source_obj.filePattern))
            file_name_list = glob.glob(path_name) + glob.glob(zipped_path_name) + glob.glob(gzipped_path_name)

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
