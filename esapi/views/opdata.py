# -*- coding: utf-8 -*-


from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import ESQueryDateParametersDoesNotExist, FondefVizError, ESQueryResultEmpty
from esapi.helper.opdata import ESOPDataHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from esapi.utils import get_dates_from_request
from localinfo.helper import get_calendar_info, PermissionBuilder
from localinfo

class OPDataByAuthRouteCode(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(OPDataByAuthRouteCode, self).dispatch(request, *args, **kwargs)

    def transalate_route(self, auth_route_code):

        return '101I'

    def transform_data(self, query):
        return '1'

    def process_request(self, request, params, export_data=False):
        response = {}
        dates = get_dates_from_request(request, export_data)
        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist

            code = self.transalate_route(request['authRouteCode'])
            es_helper = ESOPDataHelper()
            es_query = es_helper.get_route_info(code, dates)
            data = self.transform_data(es_query)
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
