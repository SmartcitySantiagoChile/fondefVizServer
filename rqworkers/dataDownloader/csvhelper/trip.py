# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.csvhelper.helper import ZipManager, TripCSVHelper


class TripData(object):
    """ Class that represents a trip csv file. """

    def __init__(self, es_client, es_query):
        self.es_query = es_query
        self.es_client = es_client

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        trip_file = TripCSVHelper(self.es_client, self.es_query)
        trip_file.download(zip_manager)

        template = 'trip.readme'
        data_filter = trip_file.get_filter_criteria()
        files_description = [trip_file.get_file_description()]
        zip_manager.build_readme(template, "\r\n".join(files_description), data_filter)
