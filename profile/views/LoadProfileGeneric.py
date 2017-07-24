from django.views.generic import View
from django.conf import settings

from elasticsearch_dsl import Search, A, MultiSearch


class LoadProfileGeneric(View):
    ''' generic view to load profile data'''

    # elastic search index name 
    INDEX_NAME="profiles"

    def __init__(self, additionalESQueryDict):
        ''' contructor '''
        esQueryDict = self.getDefaultESQueryDict()
        esQueryDict.update(additionalESQueryDict)
        
        self.context= self.getESQueryResult(esQueryDict)

    def getESQueryResult(self, esQueryDict):
        ''' retrieve all data available in elasticsearch'''
        client = settings.ES_CLIENT

        multiSearch = MultiSearch(using=client, index=self.INDEX_NAME)
  
        keys = []
        for key, esQuery in esQueryDict.iteritems():
          multiSearch = multiSearch.add(esQuery)
          keys.append(key)

        # to see the query generated
        #print multiSearch.to_dict()
        responses = multiSearch.execute()

        result = {}
        for index, response in enumerate(responses):
          resultList = []
          for tag in response.aggregations.unique.buckets:
            resultList.append(tag.key)
          resultList.sort()

          result[keys[index]] = resultList
        
        return result

    def getDefaultESQueryDict(self):
        ''' create a dict of elastic search query '''

        esTimePeriodQuery = Search()
        esTimePeriodQuery = esTimePeriodQuery[:0]
        aggs = A('terms', field = "timePeriodInStartTime", size=50)
        esTimePeriodQuery.aggs.bucket('unique', aggs)

        esDayTypeQuery = Search()
        esDayTypeQuery = esDayTypeQuery[:0]
        aggs = A('terms', field = "dayType", size=10)
        esDayTypeQuery.aggs.bucket('unique', aggs)
 
        result = {}
        result['periods'] = esTimePeriodQuery
        result['dayTypes'] = esDayTypeQuery

        return result

