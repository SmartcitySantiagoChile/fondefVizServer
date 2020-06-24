from django.core.management.base import BaseCommand

from esapi.helper.shape import ESShapeHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.opdata import ESOPDataHelper
from localinfo import helper
import itertools
from collections import defaultdict

from esapi.helper.stopbyroute import ESStopByRouteHelper


class Command(BaseCommand):
    help = 'Verify consistency between operation program data'

    def handle(self, *args, **options):

        # check if exist the same dates
        shape_helper = ESShapeHelper()
        stop_helper = ESStopHelper()
        opdata_helper = ESOPDataHelper()
        stop_by_route = ESStopByRouteHelper()
        dates = defaultdict(lambda: {'shape': False, 'stop': False, 'opdata': False})
        for shape_date in shape_helper.get_available_days():
            dates[shape_date]['shape'] = True
        for stop_date in stop_helper.get_available_days():
            dates[stop_date]['stop'] = True
        for opdata_date in opdata_helper.get_available_days():
            dates[opdata_date]['opdata'] = True

        for date in dates.keys():
            finish = False
            if not dates[date]['shape']:
                self.stdout.write('Missing {0} date in Shape'.format(date))
                finish = True
            if not dates[date]['stop']:
                self.stdout.write('Missing {0} date in Stop'.format(date))
                finish = True
            if not dates[date]['opdata']:
                self.stdout.write('Missing {0} date in OPData'.format(date))
                finish = True

            if finish:
                return

        # validation
        for date in dates.keys():
            shape_query = shape_helper.get_data_from_date(date).execute()
            for hit in shape_query.hits:

                auth_route_code = hit['authRouteCode']
                try:
                    stop_list = stop_by_route.get_stop_list(auth_route_code, [[date]])
                    print('Exist stop:', auth_route_code)
                except Exception as e:
                    print('Error stop:', auth_route_code)

                op_route_code = helper.get_op_route(auth_route_code)
                print(op_route_code)
                try:
                    data_list = opdata_helper.get_route_info(op_route_code, [[date]])
                    print('Exist opdata:', auth_route_code)
                except Exception as e:
                    print('Error opdata:', auth_route_code)

