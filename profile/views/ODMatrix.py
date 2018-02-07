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

        day = request.GET.get('day')
        dayType = request.GET.getlist('dayType[]')
        period = request.GET.getlist('period[]')
        route = request.GET.get('route')

        response = {}
        response['data'] = {}
        try:
            if not route:
                raise ESQueryRouteParameterDoesNotExist()

            matrix, max_value = self.es_od_helper.ask_for_od(route, period, dayType, day)
            stop_list = self.es_stop_helper.get_stop_list(route, day,
                                                          fields=['userStopCode', 'stopName', 'authStopCode',
                                                                  'order'])

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
