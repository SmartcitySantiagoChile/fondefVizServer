# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.conf import settings

from esapi.helper.resume import ESResumeStatisticHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.profile import ESProfileHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.trip import ESTripHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.stop import ESStopHelper

import os


class Command(BaseCommand):
    help = 'Create index to upload data to elasticsearch'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        helpers = [
            ESStopHelper(),
            ESStopByRouteHelper(),
            ESProfileHelper(),
            ESSpeedHelper(),
            ESTripHelper(),
            ESShapeHelper(),
            ESODByRouteHelper(),
            ESResumeStatisticHelper()
        ]

        def get_mapping_file(helper):
            current_dir = os.path.dirname(__file__)
            path_to_mapping_files = os.path.join(current_dir, '..', '..', '..', 'rqworkers', 'dataUploader', 'mappings')
            mapping_file = os.path.join(path_to_mapping_files, '{0}-template.json'.format(helper.index_name))
            return mapping_file

        for helper in helpers:
            # Create index with mapping. If it already exists, ignore this
            with open(get_mapping_file(helper), 'r') as mapping:
                settings.ES_CLIENT.indices.create(index=helper.index_name, ignore=400, body=mapping.read())
                self.stdout.write(self.style.SUCCESS('Index {0} created successfully'.format(helper.index_name)))
