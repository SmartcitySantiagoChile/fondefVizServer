from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from esapi.errors import ESQueryDateParametersDoesNotExist, FondefVizError, ESQueryResultEmptyRoute
from esapi.helper.opdata import ESOPDataHelper
from esapi.utils import get_dates_from_request
from localinfo.helper import get_timeperiod_list_for_select_input


class OPDataByAuthRouteCode(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(OPDataByAuthRouteCode, self).dispatch(request, *args, **kwargs)

    def transform_data(self, query):
        time_period_dict = get_timeperiod_list_for_select_input(to_dict=True)
        for hit in query.execute():
            res = list(map(lambda x: x.to_dict(), list(hit.dayType)))
            res = sorted(res, key=lambda x: x['timePeriod'])
            dict_res = {}
            for data_dict in res:
                time_period_id = data_dict['timePeriod']
                data_dict['timePeriod'] = time_period_dict[data_dict['timePeriod']]
                dict_res[time_period_id] = data_dict
            return dict_res

    def process_request(self, request, params, export_data=False):
        response = {}
        dates = get_dates_from_request(request, export_data)
        op_route_code = request.GET['opRouteCode']
        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist

            es_helper = ESOPDataHelper()
            es_query = es_helper.get_route_info(op_route_code, dates)
            data = self.transform_data(es_query)
            if not data:
                raise ESQueryResultEmptyRoute(op_route_code)
            response = {
                'data': data,
            }
        except FondefVizError as e:
            response['status'] = e.get_status_response()
        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)
