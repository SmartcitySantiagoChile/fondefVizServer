from django.core.management.base import BaseCommand

from esapi.helper.shape import ESShapeHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.opdata import ESOPDataHelper
import itertools



class Command(BaseCommand):
    help = 'Verify consistency between operation program data'

    def handle(self, *args, **options):
        shape_helper = ESShapeHelper()
        stop_helper = ESStopHelper()
        opdata_helper = ESOPDataHelper()
        dates = {
            'shape': shape_helper.get_available_days(),
            'stop': stop_helper.get_available_days(),
            'opdata': opdata_helper.get_available_days()
        }

        for (shape_date, stop_date, opdata_date) in zip(dates['shape'], dates['stop'], dates['opdata']):
            min_date = min(shape_date, stop_date, opdata_date)
            correct = True
            if shape_date != min_date:
                self.stdout.write('Missing {0} date in Shape')
            print(min_date)
