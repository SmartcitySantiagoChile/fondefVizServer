import os

from django.conf import settings
from django.core.management.base import BaseCommand

from esapi.helper.bip import ESBipHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.opdata import ESOPDataHelper
from esapi.helper.paymentfactor import ESPaymentFactorHelper
from esapi.helper.profile import ESProfileHelper
from esapi.helper.resume import ESResumeStatisticHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.stage import ESStageHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.trip import ESTripHelper


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
            ESResumeStatisticHelper(),
            ESPaymentFactorHelper(),
            ESBipHelper(),
            ESOPDataHelper(),
            ESStageHelper()
        ]

        def get_mapping_file(helper):
            path_to_mapping_files = os.path.join(settings.BASE_DIR, 'dataUploader', 'datauploader', 'mappings')
            mapping_file = os.path.join(path_to_mapping_files, '{0}-template.json'.format(helper.index_name))
            return mapping_file

        for helper in helpers:
            # Create index with mapping. If it already exists, ignore this
            with open(get_mapping_file(helper), 'r') as mapping:
                settings.ES_CLIENT.indices.create(index=helper.index_name, ignore=400, body=mapping.read())
                self.stdout.write(self.style.SUCCESS('Index {0} created successfully'.format(helper.index_name)))
