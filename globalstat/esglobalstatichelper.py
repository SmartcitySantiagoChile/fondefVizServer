from bowerapp.eshelper.eshelper import ElasticSearchHelper

class ESGlobalStaticHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "general"
        super(ESGlobalStaticHelper, self).__init__(index_name)

    def get_form_data(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """


        esDateQuery = self.get_histogram_query("date", interval="day", format="yyy-MM-dd")

        result = {}
        result['dates'] = esDateQuery

        return self.make_multisearch_query_for_aggs(result)
