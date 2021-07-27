from datetime import datetime

from esapi.helper.basehelper import ElasticSearchHelper


class ESStageHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "stage"
        file_extensions = ['etapas']
        super(ESStageHelper, self).__init__(index_name, file_extensions)

    def get_available_days(self, valid_operator_list):
        return self._get_available_days('boardingTime', valid_operator_list)

    def get_available_days_between_dates(self, start_date, end_date, valid_operator_list=None):
        date_format = '%Y-%m-%d'
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        days_in_between = []
        days = self._get_available_days('boardingTime', valid_operator_list)
        for day in days:
            day_obj = datetime.strptime(day, date_format)
            if start_date <= day_obj <= end_date:
                days_in_between.append(day)
        return days_in_between
