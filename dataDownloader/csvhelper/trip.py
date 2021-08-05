from django.conf import settings

from dataDownloader.csvhelper.helper import ZipManager, TripCSVHelper, PostProductTripTripBetweenZonesCSVHelper, \
    PostProductTripBoardingAndAlightingCSVHelper


class TripData(object):
    """ Class that represents a trip csv file. """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.trip_file = TripCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.trip_file.get_filter_criteria(TripCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.trip_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE VIAJES'
        data_filter = self.trip_file.get_filter_criteria(TripCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.trip_file.get_file_description()]
        explanation = self.trip_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)


class PostProductTripTripBetweenZonesData(object):

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.trip_file = PostProductTripTripBetweenZonesCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.trip_file.get_filter_criteria(PostProductTripTripBetweenZonesCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.trip_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE VIAJES'
        data_filter = self.trip_file.get_filter_criteria(PostProductTripTripBetweenZonesCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.trip_file.get_file_description()]
        explanation = self.trip_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)


class PostProductTripBoardingAndAlightingData(object):

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.trip_file = PostProductTripBoardingAndAlightingCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.trip_file.get_filter_criteria(PostProductTripBoardingAndAlightingCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.trip_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE VIAJES'
        data_filter = self.trip_file.get_filter_criteria(
            PostProductTripBoardingAndAlightingCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.trip_file.get_file_description()]
        explanation = self.trip_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)
