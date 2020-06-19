# -*- coding: utf-8 -*-


from esapi.helper.basehelper import ElasticSearchHelper


class ESOpDataHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'opdata'
        file_extensions = ['opdata']
        super(ESOpDataHelper, self).__init__(index_name, file_extensions)

