from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse

from errors import ESQueryParametersDoesNotExist, ESQueryRouteParameterDoesNotExist, ESQueryResultEmpty
from profile.esprofilehelper import ESODByRouteHelper, ESStopHelper

from localinfo.models import HalfHour


class ODMatrixView(View):
    def __init__(self):
        """ Constructor """
        super(ODMatrixView, self).__init__()

        self.es_helper = ESODByRouteHelper()
        self.base_params = self.es_helper.get_base_params()

    def get(self, request):
        template = "profile/odmatrix.html"

        # add periods of thirty minutes
        minutes = HalfHour.objects.all().order_by("id").values_list("longName", flat=True)

        context = self.es_helper.make_multisearch_query_for_aggs(self.base_params)
        context['minutes'] = minutes

        return render(request, template, context)


class GetODMatrixData(View):

    def __init__(self):
        """ constructor """
        super(GetODMatrixData, self).__init__()
        self.es_od_helper = ESODByRouteHelper()
        self.es_stop_helper = ESStopHelper()
        self.context = {}

    def get(self, request):
        """ data data """

        startDate = request.GET.get('startDate')
        endDate = request.GET.get('endDate')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        route = request.GET.get('authRoute')

        response = {}
        response['data'] = {}
        try:
            if not route:
                raise ESQueryRouteParameterDoesNotExist()

            startDate = startDate[:10]
            endDate = endDate[:10]
            matrix, max_value = self.es_od_helper.ask_for_od(route, period, dayType, startDate, endDate)
            stop_list = self.es_stop_helper.get_stop_list(route, startDate,
                                                          fields=['userStopCode', 'stopName', 'authStopCode', 'order'])

            # esQuery = self.buildQuery(request)
            # response['trips'] = self.transformESAnswer(esQuery)
            response["data"] = {
                "matrix": matrix,
                "maximum": max_value,
                "stopList": stop_list
            }

            # debug
            # response['query'] = esQuery.to_dict()
            # return JsonResponse(response, safe=False)
            # response['state'] = {'success': answer.success(), 'took': answer.took, 'total': answer.hits.total}
        except (ESQueryRouteParameterDoesNotExist, ESQueryParametersDoesNotExist, ESQueryResultEmpty) as e:
            response['status'] = e.getStatusResponse()

        return JsonResponse(response, safe=False)


class GetODAvailableDays(View):

    def get(self, request):
        self.es_helper = ESODByRouteHelper()
        available_days = self.es_helper.ask_for_available_days()

        response = {}
        response['availableDays'] = available_days

        return JsonResponse(response)


class GetODAvailableRoutes(View):

    def get(self, request):
        self.es_helper = ESODByRouteHelper()
        available_days, op_dict = self.es_helper.ask_for_available_routes()

        response = {}
        response['availableRoutes'] = available_days
        response['operatorDict'] = op_dict

        return JsonResponse(response)
