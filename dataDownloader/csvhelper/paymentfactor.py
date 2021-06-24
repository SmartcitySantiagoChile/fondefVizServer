from django.conf import settings

from dataDownloader.csvhelper.helper import ZipManager, PaymentFactorCSVHelper


class PaymentFactorData(object):
    """ Class that represents a bus station distribution csv file. """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.bus_station_dist_file = PaymentFactorCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.bus_station_dist_file.get_filter_criteria(PaymentFactorCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.bus_station_dist_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE DISTRIBUCIÓN DE VALIDACIONES EN ZONA PAGA'
        data_filter = self.bus_station_dist_file.get_filter_criteria(PaymentFactorCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.bus_station_dist_file.get_file_description()]
        explanation = self.bus_station_dist_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)
