from django.http import JsonResponse
from django.views import View

from esapi.errors import ESQueryStopPatternTooShort, FondefVizError
from esapi.helper.stop import ESStopHelper


class MatchedStopData(View):
    """ it gives a stop list with stops that match with patter given by user """

    def get(self, request):

        term = request.GET.get("term", '')
        date = request.GET.get("date", None)

        response = {
            'items': []
        }
        try:
            if len(term) < 3:
                raise ESQueryStopPatternTooShort()

            es_helper = ESStopHelper()
            results = es_helper.get_matched_stop_list(term, date)

            result_list = []
            for text, text_id in results:
                result_list.append({"id": text_id, "text": text})

            response['items'] = result_list
        except ESQueryStopPatternTooShort as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)


class StopInfo(View):
    """ Give a stop info based on stop name and date"""
    def get(self, request):
        stop_name = request.GET.get("stop", '')
        stop_date = request.GET.get("date", None)
        response = {
            'info': []
        }
        try:
            es_helper = ESStopHelper()
            results = es_helper.get_stop_info([[stop_date]], stop_name)
            response["info"] = results
        except FondefVizError as e:
            response['status'] = e.get_status_response()
        return JsonResponse(response, safe=False)


