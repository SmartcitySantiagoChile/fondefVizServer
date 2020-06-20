# -*- coding: utf-8 -*-
from esapi.errors import ESQueryDateRangeParametersDoesNotExist, ESQueryOperationProgramDoesNotExist, \
    ESQueryThereIsMoreThanOneOperationProgram
from esapi.helper.basehelper import ElasticSearchHelper


class ESOPDataHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'opdata'
        file_extensions = ['opdata']
        super(ESOPDataHelper, self).__init__(index_name, file_extensions)

    def check_operation_program_between_dates(self, start_date, end_date):
        """
        Check that there is not exist operation program between start date and end date, and if exists it has to be
        equal to start date

        :param start_date: lower date bound
        :param end_date: upper date bound
        :return: None
        """
        es_query = self.get_base_query().filter('range', startDate={
            'gte': start_date,
            'lte': end_date,
            'format': 'yyyy-MM-dd'
        })
        es_query = self.get_unique_list_query("startDate", size=5000, query=es_query)
        dates = [x.key_as_string[:10] for x in es_query.execute().aggregations.unique.buckets]
        days_quantity = len(dates)

        if days_quantity == 0:
            # check if there is operation program previous to start_Date
            es_query = self.get_base_query().filter('range', startDate={
                'lt': start_date,
                'format': 'yyyy-MM-dd'
            })
            es_query = self.get_unique_list_query("startDate", size=5000, query=es_query)
            if len(es_query.execute().aggregations.unique.buckets) == 0:
                raise ESQueryOperationProgramDoesNotExist(start_date, end_date)
        elif days_quantity > 1 or (days_quantity == 1 and start_date != dates[0]):
            raise ESQueryThereIsMoreThanOneOperationProgram(start_date, end_date, dates)


    def get_route_info(self, op_route_code, dates):
        return None