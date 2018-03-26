# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from rqworkers.dataDownloader.csvhelper.helper import ZipManager, TripCSVHelper


class TripData(object):
    """ Class that represents a trip csv file. """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.trip_file = TripCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.trip_file.get_filter_criteria()

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.trip_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE VIAJES'
        data_filter = self.trip_file.get_filter_criteria()
        files_description = [self.trip_file.get_file_description()]
        explanation = self.trip_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)

