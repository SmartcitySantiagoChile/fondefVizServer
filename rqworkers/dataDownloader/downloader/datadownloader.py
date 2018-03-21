# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search

from rqworkers.dataDownloader.unicodecsv import UnicodeWriter

from localinfo.helper import get_day_type_list_for_select_input, get_timeperiod_list_for_select_input, \
    get_operator_list_for_select_input, get_halfhour_list_for_select_input

from rqworkers.dataDownloader.errors import FilterHasToBeListErrpr

import os
import zipfile
import uuid

README_FILE_NAME = 'Léeme.txt'


class DataDownloader:

    def __init__(self, es_query):
        self.es_query = es_query

        self.operator_dict = get_operator_list_for_select_input(to_dict=True)
        self.day_type_dict = get_day_type_list_for_select_input(to_dict=True)
        self.timeperiod_dict = get_timeperiod_list_for_select_input(to_dict=True)
        self.halfhour_dict = get_halfhour_list_for_select_input(to_dict=True, format='name')

        self.column_dict = [
            {'es_name': '', 'csv_name': ''}
        ]
        self.translator = self.create_translator()

    def download(self, es_client, index_name, zip_file, chunk_size, timeout):
        # create zipfile
        with zipfile.ZipFile(zip_file, 'w') as zip_file_obj:
            tmp_file_name = str(uuid.uuid4())
            try:
                with open(tmp_file_name, 'wb') as output:
                    writter = UnicodeWriter(output, delimiter=str(','))
                    writter.writerow(self.get_header())
                    es_query = Search(using=es_client, index=index_name).update_from_dict(self.es_query)
                    es_query = es_query.source(self.get_fields())
                    es_query.params = {'request_timeout': timeout, 'size': chunk_size}
                    for doc in es_query.scan():
                        writter.writerow(self.row_parser(doc))

                zip_file_obj.write(tmp_file_name, arcname=self.get_data_file_name())
            finally:
                os.remove(tmp_file_name)

            self.add_additional_files(zip_file_obj)

    def create_translator(self):
        """ create dict with structure es_name: csv_name """
        return {x['es_name']: x['csv_name'] for x in self.column_dict}

    def get_filter_criteria(self):
        """ return list used to put in readme file to specify filters applied over data """
        formatted_filters = []
        filters = self.es_query['query']['bool']['filter']

        if not isinstance(filters, list):
            raise FilterHasToBeListErrpr()

        for filter in filters:
            if 'term' in filter:
                field = filter['term'].keys()[0]
                value = filter['term'][field]
                field = field.split('.')[0]

                line = '\t\t- {0}: {1}'.format(self.translator[field], value)
                formatted_filters.append(line)
            elif 'terms' in filter:
                # ignore operator filter
                if 'operator' in filter['terms']:
                    continue
                field = filter['terms'].keys()[0]
                values = filter['terms'][field]

                if field == 'dayType':
                    values = [self.day_type_dict[x] for x in values]
                elif field in ['timePeriodInStartTime', 'timePeriodInStopTime']:
                    values = [self.timeperiod_dict[x] for x in values]
                elif field in ['halfHourInStartTime', 'halfHourInStopTime']:
                    values = [self.halfhour_dict[x] for x in values]

                line = '\t\t- {0}:'.format(self.translator[field])
                formatted_filters.append(line)
                for value in values:
                    line = '\t\t\t{0}'.format(value)
                    formatted_filters.append(line)
            elif 'range' in filter:
                field = filter['range'].keys()[0]
                gte = filter['range'][field]["gte"].replace("||/d", "")
                lte = filter['range'][field]["lte"].replace("||/d", "")

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
