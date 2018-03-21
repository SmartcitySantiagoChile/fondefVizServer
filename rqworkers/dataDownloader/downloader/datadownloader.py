# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch_dsl import Search

import csv
import zipfile
import json

README_FILE_NAME = 'Léeme.txt'


class DataDownloader:

    def __init__(self):
        pass

    def download(self, es_client, es_query, index_name, zip_file, chunk_size, timeout):
        # create zipfile
        with zipfile.ZipFile(zip_file, 'w') as zip_file_obj:
            with zip_file_obj.write(self.get_data_file_name(), 'w') as output:
                writter = csv.writer(output)
                writter.writerow(self.get_header())
                es_query = Search(using=es_client, index=index_name).update_from_dict(json.loads(es_query))
                es_query.source(self.get_fields())
                for doc in es_query.scan(params={'request_timeout': timeout, 'size': chunk_size}):
                    writter.writerow(self.row_parser(doc))

            self.add_additional_files(zip_file_obj)

    def row_parser(self, row):
        raise NotImplementedError()

    def get_data_file_name(self):
        """ get data file name where will save main file """
        raise NotImplementedError()

    def get_header(self):
        """ get header of csv file """
        raise NotImplementedError()

    def get_fields(self):
        """ get fields retrieved by query """
        raise NotImplementedError()

    def add_additional_files(self, zip_file_obj):
        """ add additional files to zip file as help file or stop file or shape file """
        raise NotImplementedError()