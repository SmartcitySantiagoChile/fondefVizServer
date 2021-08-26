from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

import dataDownloader.csvhelper.helper as csv_helper
from datamanager.helper import ExporterManager
from esapi.errors import FondefVizError, ESQueryDateParametersDoesNotExist
from esapi.helper.stage import ESStageHelper
from esapi.messages import ExporterDataHasBeenEnqueuedMessage
from esapi.utils import get_dates_from_request
from localinfo.helper import PermissionBuilder, get_calendar_info


class AvailableDays(View):

    def get(self, request):
        es_helper = ESStageHelper()
        valid_operator_list = PermissionBuilder().get_valid_operator_id_list(request.user)
        available_days = es_helper.get_available_days(valid_operator_list)
        calendar_info = get_calendar_info()
        response = {
            'availableDays': available_days,
            'info': calendar_info
        }

        return JsonResponse(response)


@method_decorator([csrf_exempt], name='dispatch')
class PostProductTransfersData(View):

    def process_request(self, request, params, export_data=False):
        dates = get_dates_from_request(request, export_data)
        day_types = params.getlist('dayType[]', [])
        communes = params.getlist('communes[]', [])
        aggregate_data = params.get('exportButton2', False)

        response = {}

        es_stage_helper = ESStageHelper()

        try:
            if not dates or not isinstance(dates[0], list) or not dates[0]:
                raise ESQueryDateParametersDoesNotExist
            if export_data:
                if aggregate_data:
                    es_query = es_stage_helper.get_post_products_aggregated_transfers_data_query(dates, day_types,
                                                                                                 communes)
                    ExporterManager(es_query).export_data(csv_helper.POST_PRODUCTS_STAGE_TRANSFERS_AGGREGATED_DATA,
                                                          request.user)
                else:
                    es_query = es_stage_helper.get_post_products_transfers_data_query(dates, day_types, communes)
                    ExporterManager(es_query).export_data(csv_helper.POST_PRODUCTS_STAGE_TRANSFERS_DATA, request.user)
                response['status'] = ExporterDataHasBeenEnqueuedMessage().get_status_response()
            else:
                pass
        except FondefVizError as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response)

    def post(self, request):
        return self.process_request(request, request.POST, export_data=True)
