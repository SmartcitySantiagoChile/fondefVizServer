# -*- coding: utf-8 -*-


from django.conf import settings

from dataDownloader.csvhelper.helper import ZipManager, BipCSVHelper


class BipData(object):
    """ class that build profile csv """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.bip_file = BipCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.bip_file.get_filter_criteria(BipCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.bip_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE BIPS'
        data_filter = self.bip_file.get_filter_criteria(BipCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.bip_file.get_file_description()]
        explanation = self.bip_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)
