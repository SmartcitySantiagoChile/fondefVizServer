from django.conf import settings

from dataDownloader.csvhelper.helper import ZipManager, PostProductsStageTransferInPeriodCSVHelper, \
    PostProductsStageTransferInPeriodGroupedByDateCSVHelper


class PostProductStageTransferData(object):
    """ Class that represents a aggregated stage csv file. """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.post_product_file = PostProductsStageTransferInPeriodCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.post_product_file.get_filter_criteria(PostProductsStageTransferInPeriodCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.post_product_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE ETAPAS AGRUPANDO TRANSBORDOS'
        data_filter = self.post_product_file.get_filter_criteria(
            PostProductsStageTransferInPeriodCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.post_product_file.get_file_description()]
        explanation = self.post_product_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)


class PostProductStageTransferAggregatedData(object):
    """ Class that represents a aggregated stage csv file. """

    def __init__(self, es_query, es_client=None):
        self.es_query = es_query
        self.es_client = settings.ES_CLIENT if es_client is None else es_client
        self.post_product_file = PostProductsStageTransferInPeriodGroupedByDateCSVHelper(self.es_client, self.es_query)

    def get_filters(self):
        return self.post_product_file.get_filter_criteria(
            PostProductsStageTransferInPeriodGroupedByDateCSVHelper.FORMATTER_FOR_WEB)

    def build_file(self, file_path):
        zip_manager = ZipManager(file_path)
        self.post_product_file.download(zip_manager)

        help_file_title = 'ARCHIVO DE ETAPAS AGRUPANDO TRANSBORDOS'
        data_filter = self.post_product_file.get_filter_criteria(
            PostProductsStageTransferInPeriodGroupedByDateCSVHelper.FORMATTER_FOR_FILE)
        files_description = [self.post_product_file.get_file_description()]
        explanation = self.post_product_file.get_field_explanation()
        zip_manager.build_readme(help_file_title, "\r\n".join(files_description), data_filter, explanation)
