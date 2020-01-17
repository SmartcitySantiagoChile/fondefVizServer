from functools import reduce

from elasticsearch_dsl import Q

from esapi.errors import ESQueryDateRangeParametersDoesNotExist
from esapi.helper.basehelper import ElasticSearchHelper


class ESResumeStatisticHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'general'
        file_extensions = ['general']
        super(ESResumeStatisticHelper, self).__init__(index_name, file_extensions)

    def get_available_days(self):
        return self._get_available_days('date')

    def get_data(self, dates, metrics):
        if len(metrics) == 0:
            metrics = ['transactionWithoutRoute', 'transactionWithRoute', 'transactionNumber',
                       'transactionOnTrainNumber', 'transactionOnMetroNumber', 'transactionOnBusNumber',
                       'transactionOnBusStation', 'averageVelocityInAfternoonRushTrips',
                       'averageTimeInAfternoonRushTrips', 'averageDistanceInAfternoonRushTrips',
                       'tripNumberInAfternoonRushHour', 'averageVelocityInMorningRushTrips',
                       'averageTimeInMorningRushTrips', 'averageDistanceInMorningRushTrips',
                       'tripNumberInMorningRushHour', 'licensePlateNumber', 'GPSPointsNumber', 'GPSNumberWithRoute',
                       'GPSNumberWithoutRoute', 'expeditionNumber', 'maxExpeditionTime', 'minExpeditionTime',
                       'averageExpeditionTime', 'smartcardNumber', 'tripNumber', 'averageTimeOfTrips',
                       'averageVelocityOfTrips', 'averageTimeBetweenGPSPoints', 'averageDistanceOfTrips',
                       'tripsThatUseMetro', 'completeTripNumber', 'stagesWithBusStationAlighting',
                       'tripsWithoutLastAlighting', 'validTripNumber', 'tripsWithOneStage', 'tripsWithTwoStages',
                       'tripsWithThreeStages', 'tripsWithFourStages', 'tripsWithFiveOrMoreStages', 'tripsWithOnlyMetro',
                       'stagesWithBusAlighting', 'stagesWithTrainAlighting', 'stagesWithMetroAlighting', 'dayType',
                       'version', 'transactionInMorningRushHour', 'transactionInAfternoonRushHour', 'alightingNumber',
                       'alightingNumberInMorningRushHour', 'alightingNumberInAfternoonRushHour', 'stopsNumberWithTypeE',
                       'stopsNumberWithTypeT', 'stopsNumberWithTypeL', 'stopsNumberWithTypeI',
                       'transactionNumberInStopsWithTypeE', 'transactionNumberInStopsWithTypeT',
                       'transactionNumberInStopsWithTypeL', 'transactionNumberInStopsWithTypeI',
                       'firstStopWithMoreValidations', 'secondStopWithMoreValidations', 'thirdStopWithMoreValidations',
                       'fourthStopWithMoreValidations', 'fifthStopWithMoreValidations', 'sixthStopWithMoreValidations',
                       'seventhStopWithMoreValidations', 'eighthStopWithMoreValidations',
                       'ninethStopWithMoreValidations', 'tenthStopWithMoreValidations',
                       'transactionNumberInFirstStopWithMoreValidations',
                       'transactionNumberInSecondStopWithMoreValidations',
                       'transactionNumberInThirdStopWithMoreValidations',
                       'transactionNumberInFourthStopWithMoreValidations',
                       'transactionNumberInFifthStopWithMoreValidations',
                       'transactionNumberInSixthStopWithMoreValidations',
                       'transactionNumberInSeventhStopWithMoreValidations',
                       'transactionNumberInEighthStopWithMoreValidations',
                       'transactionNumberInNinethStopWithMoreValidations',
                       'transactionNumberInTenthStopWithMoreValidations',
                       'firstBusStopWithMoreValidations', 'secondBusStopWithMoreValidations',
                       'thirdBusStopWithMoreValidations', 'fourthBusStopWithMoreValidations',
                       'fifthBusStopWithMoreValidations', 'sixthBusStopWithMoreValidations',
                       'seventhBusStopWithMoreValidations', 'eighthBusStopWithMoreValidations',
                       'ninethBusStopWithMoreValidations', 'tenthBusStopWithMoreValidations',
                       'transactionNumberInFirstBusStopWithMoreValidations',
                       'transactionNumberInSecondBusStopWithMoreValidations',
                       'transactionNumberInThirdBusStopWithMoreValidations',
                       'transactionNumberInFourthBusStopWithMoreValidations',
                       'transactionNumberInFifthBusStopWithMoreValidations',
                       'transactionNumberInSixthBusStopWithMoreValidations',
                       'transactionNumberInSeventhBusStopWithMoreValidations',
                       'transactionNumberInEighthBusStopWithMoreValidations',
                       'transactionNumberInNinethBusStopWithMoreValidations',
                       'transactionNumberInTenthBusStopWithMoreValidations',
                       ]
        es_query = self.get_base_query()

        es_query = es_query.source(['date'] + metrics)
        combined_filter = []
        for date_range in dates:
            start_date = date_range[0]
            end_date = date_range[len(date_range) - 1]
            if not start_date or not end_date:
                raise ESQueryDateRangeParametersDoesNotExist()
            filter_q = Q('range', date={
                'gte': start_date + '||/d',
                'lte': end_date + '||/d',
                'format': 'yyyy-MM-dd',
                'time_zone': '+00:00'
            })
            combined_filter.append(filter_q)
        combined_filter = reduce((lambda x, y: x | y), combined_filter)
        es_query = es_query.query('bool', filter=[combined_filter])
        return es_query
