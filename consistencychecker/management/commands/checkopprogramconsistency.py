from collections import defaultdict

from django.core.management.base import BaseCommand

from esapi.errors import ESQueryStopListDoesNotExist, ESQueryRouteParameterDoesNotExist
from esapi.helper.opdata import ESOPDataHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from localinfo import helper


class Command(BaseCommand):
    help = 'Verify consistency between operation program data'

    def handle(self, *args, **options):

        # check if exist the same dates
        shape_helper = ESShapeHelper()
        stop_helper = ESStopHelper()
        opdata_helper = ESOPDataHelper()
        stop_by_route = ESStopByRouteHelper()
        dates = defaultdict(
            lambda: {'shape': {'status': False, 'missing': []}, 'stop': {'status': False, 'missing': []},
                     'opdata': {'status': False, 'missing': []}})
        for shape_date in shape_helper.get_available_days():
            dates[shape_date]['shape']['status'] = True
        for stop_date in stop_helper.get_available_days():
            dates[stop_date]['stop']['status'] = True
        for opdata_date in opdata_helper.get_available_days():
            dates[opdata_date]['opdata']['status'] = True
        finish = False
        for date in sorted(dates.keys()):
            if not dates[date]['shape']['status']:
                self.stdout.write('Missing {0} date in Shape'.format(date))
                finish = True

            if not dates[date]['stop']['status']:
                self.stdout.write('Missing {0} date in Stop'.format(date))
                finish = True

            if not dates[date]['opdata']['status']:
                self.stdout.write('Missing {0} date in OPData'.format(date))
                finish = True

        if finish:
            return
        else:
            self.stdout.write('All dates checked successfully!')

        # validation
        for date in dates.keys():
            shape_query = shape_helper.get_data_from_date(date).execute()
            for hit in shape_query.hits:
                auth_route_code = hit['authRouteCode']
                print(auth_route_code)
                try:
                    stop_list = stop_by_route.get_stop_list(auth_route_code, [[date]])
                except ESQueryStopListDoesNotExist as e:
                    dates[date]['stop']['missing'].append(auth_route_code)

                op_route_code = helper.get_op_route(auth_route_code)
                try:
                    data_list = opdata_helper.get_route_info(op_route_code, [[date]])
                except ESQueryRouteParameterDoesNotExist as e:
                    dates[date]['opdata']['missing'].append(auth_route_code)
            print("Missing auth codes in stop: {0}".format(dates[date]['stop']['missing']))
            print("Missing auth codes in opdata: {0}".format(dates[date]['opdata']['missing']))
