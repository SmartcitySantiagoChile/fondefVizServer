# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from esapi.errors import FondefVizError, ESQueryOperationProgramError, ESQueryDateRangeParametersDoesNotExist
from esapi.helper.shape import ESShapeHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper


def check_operation_program(start_date, end_date):
    """
    Check if operation program is valid between dates

    :param start_date: lower date bound
    :param end_date: upper date bound
    :return: None
    """
    if not start_date or not end_date:
        raise ESQueryDateRangeParametersDoesNotExist()
    operation_program_error_for_stop = False
    operation_program_error_for_shape = False
    error_raised = None

    try:
        ESStopByRouteHelper().check_operation_program_between_dates(start_date, end_date)
    except FondefVizError as e:
        operation_program_error_for_stop = True
        error_raised = e

    try:
        ESShapeHelper().check_operation_program_between_dates(start_date, end_date)
    except FondefVizError as e:
        operation_program_error_for_shape = True
        error_raised = e

    if operation_program_error_for_shape != operation_program_error_for_stop:
        raise ESQueryOperationProgramError()
    elif operation_program_error_for_shape == True or operation_program_error_for_stop == True:
        raise error_raised


def get_dates_from_request(request, export_data):
    """
    Convert the GET[dates] or POST[dates] JSON to list
    :param request: http request
    :param export_data: GET or Post
    :return: dates[] list
    """
    if not export_data:
        dates_raw = list(request.GET.items())
    else:
        dates_raw = list(request.POST.items())
    index = 0
    if dates_raw != []:
        for indexes in range(len(dates_raw)):
            if dates_raw[indexes][0] == "dates":
                index = indexes
        dates_raw = json.loads(dates_raw[index][1])
        dates_aux = []
        dates = []
        for i in dates_raw:
            for j in i:
                dates_aux.append(str(j))
            dates.append(dates_aux)
            dates_aux = []
    else:
        dates = []
    return dates
