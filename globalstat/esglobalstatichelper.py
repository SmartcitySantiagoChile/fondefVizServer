from bowerapp.eshelper.eshelper import ElasticSearchHelper

class ESGlobalStaticHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "general"
        super(ESGlobalStaticHelper, self).__init__(index_name)

    def get_form_data(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """


        esDateQuery = self.get_histogram_query("date", interval="day", format="yyy-MM-dd")
        esDayTypeQuery = self.get_unique_list_query("dayType", size=100)

        result = {}
        result['dates'] = esDateQuery
        result['dayTypes'] = esDayTypeQuery

        return self.make_multisearch_query_for_aggs(result)
