# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search

from rqworkers.dataDownloader.unicodecsv import UnicodeWriter
from rqworkers.dataDownloader.errors import FilterHasToBeListErrpr

from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_operator_list_for_select_input, get_halfhour_list_for_select_input

import os
import zipfile
import uuid

README_FILE_NAME = 'Léeme.txt'


class DataDownloader:
    # files type
    PROFILE_BY_EXPEDITION_DATA = 'profile_by_expedition'
    PROFILE_BY_STOP_DATA = 'profile_by_stop'
    OD_BY_ROUTE_DATA = 'od_by_route_data'
    SHAPE_DATA = 'shape_data'
    STOP_DATA = 'stop_data'
    SPEED_MATRIX_DATA = 'speed_matrix_data'

    def __init__(self, es_client, es_query, index_name):
        self.es_client = es_client
        self.es_query = es_query
        self.index_name = index_name

        self.operator_dict = get_operator_list_for_select_input(to_dict=True)
        self.day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        self.timeperiod_dict = get_timeperiod_list_for_select_input(to_dict=True)
        self.halfhour_dict = get_halfhour_list_for_select_input(to_dict=True, format='name')

        self.column_dict = [
            {'es_name': '', 'csv_name': ''}
        ]
        self.translator = self.create_translator()

    def download(self, zip_file, chunk_size=5000, timeout=30):
        # create zipfile
        close_zip_file = False
        if isinstance(zip_file, zipfile.ZipFile):
            zip_file_obj = zip_file
        else:
            zip_file_obj = zipfile.ZipFile(zip_file, 'w')
            close_zip_file = True

        tmp_file_name = str(uuid.uuid4())
        try:
            with open(tmp_file_name, 'wb') as output:
                writter = UnicodeWriter(output, delimiter=str(','))
                writter.writerow(self.get_header())
                es_query = Search(using=self.es_client, index=self.index_name).update_from_dict(self.es_query)
                es_query = es_query.source(self.get_fields())
                es_query.params = {'request_timeout': timeout, 'size': chunk_size}
                for doc in es_query.scan():
                    row = self.row_parser(doc)
                    if isinstance(row[0], list):
                        # there are more than one row in variable
                        writter.writerows(row)
                    else:
                        writter.writerow(row)

            zip_file_obj.write(tmp_file_name, arcname=self.get_data_file_name())
        finally:
            os.remove(tmp_file_name)

        self.add_additional_files(zip_file_obj)

        if close_zip_file:
            zip_file_obj.close()

    def create_translator(self):
        """ create dict with structure es_name: csv_name """
        return {x['es_name']: x['csv_name'] for x in self.column_dict}

    def get_filter_criteria(self):
        """ return list used to put in readme file to specify filters applied over data """
        formatted_filters = []

        if 'bool' not in self.es_query['query']:
            return ''

        filters = self.es_query['query']['bool']['filter']

        if not isinstance(filters, list):
            raise FilterHasToBeListErrpr()

        for query_filter in filters:
            if 'term' in query_filter:
                field = query_filter['term'].keys()[0]
                value = query_filter['term'][field]
                field = field.split('.')[0]

                line = '\t\t- {0}: {1}'.format(self.translator[field], value)
                formatted_filters.append(line)
            elif 'terms' in query_filter:
                # ignore operator filter
                if 'operator' in query_filter['terms']:
                    continue
                field = query_filter['terms'].keys()[0]
                values = query_filter['terms'][field]

                if field == 'dayType':
                    values = [self.day_type_dict[int(x)] for x in values]
                elif field in ['timePeriodInStartTime', 'timePeriodInStopTime']:
                    values = [self.timeperiod_dict[int(x)] for x in values]
                elif field in ['halfHourInStartTime', 'halfHourInStopTime']:
                    values = [self.halfhour_dict[int(x)] for x in values]

                line = '\t\t- {0}:'.format(self.translator[field])
                formatted_filters.append(line)
                for value in values:
                    line = '\t\t\t{0}'.format(value)
                    formatted_filters.append(line)
            elif 'range' in query_filter:
                field = query_filter['range'].keys()[0]
                gte = query_filter['range'][field]["gte"].replace("||/d", "")
                lte = query_filter['range'][field]["lte"].replace("||/d", "")

                line = '\t\t- {0}: {1} - {2}'.format(self.translator[field], gte, lte)
                formatted_filters.append(line)

        return '{0}'.format(os.linesep).join(formatted_filters)

    def row_parser(self, row):
        raise NotImplementedError()

    def get_data_file_name(self):
        """ get data file name where will save main file """
        raise NotImplementedError()

    def get_header(self):
        """ get header of csv file """
        return map(lambda el: el['csv_name'], self.column_dict)

    def get_fields(self):
        """ get fields retrieved by query """
        return map(lambda el: el['es_name'], self.column_dict)

    def add_additional_files(self, zip_file_obj):
        """ add additional files to zip file as help file or stop file or shape file """
        raise NotImplementedError()
