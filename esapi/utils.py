# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from esapi.helper.stop import ESStopHelper
from esapi.helper.shape import ESShapeHelper
from esapi.errors import FondefVizError, ESQueryOperationProgramError


def check_operation_program(start_date, end_date):
    """
    Check if operation program is valid between dates

    :param start_date: lower date bound
    :param end_date: upper date bound
    :return: None
    """
    operation_program_error_for_stop = False
    operation_program_error_for_shape = False
    error_raised = None

    try:
        ESStopHelper().check_operation_program_between_dates(start_date, end_date)
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