# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views import View

from esapi.helper.stop import ESStopHelper
from esapi.errors import ESQueryStopPatternTooShort


class MatchedStopData(View):
    """ it gives a stop list with stops that match with patter given by user """

    def get(self, request):

        term = request.GET.get("term", '')

        response = {
            'items': []
        }
        try:
            if len(term) < 3:
                raise ESQueryStopPatternTooShort()

            es_helper = ESStopHelper()
            results = es_helper.get_matched_stop_list(term)

            result_list = []
            for text, text_id in results:
                result_list.append({"id": text_id, "text": text})

            response['items'] = result_list
        except ESQueryStopPatternTooShort as e:
            response['status'] = e.get_status_response()

        return JsonResponse(response, safe=False)

