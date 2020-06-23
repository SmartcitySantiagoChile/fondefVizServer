# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from esapi.errors import ESQueryDateParametersDoesNotExist, FondefVizError, ESQueryAuthRouteCodeTranslateDoesNotExists
from esapi.helper.opdata import ESOPDataHelper
from esapi.utils import get_dates_from_request
from localinfo.helper import get_op_route


class OPDataByAuthRouteCode(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(OPDataByAuthRouteCode, self).dispatch(request, *args, **kwargs)

    def transform_data(self, query):
        return '1'

    def process_request(self, request, params, export_data=False):
        response = {}
        dates = get_dates_from_request(request, export_data)
        auth_code = request.GET['authRouteCode']
        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist

            code = get_op_route(auth_code)
            if not code:
                raise ESQueryAuthRouteCodeTranslateDoesNotExists(auth_code)

            es_helper = ESOPDataHelper()
            es_query = es_helper.get_route_info(code, dates)
            data = es_query.to_dict
            response = {
                'data': data,
            }
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

    def get(self, request):
        return self.process_request(request, request.GET)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
