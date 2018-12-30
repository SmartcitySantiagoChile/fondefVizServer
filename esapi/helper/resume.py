from esapi.helper.basehelper import ElasticSearchHelper


class ESResumeStatisticHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = 'general'
        file_extensions = ['general']
        super(ESResumeStatisticHelper, self).__init__(index_name, file_extensions)

    def get_available_days(self):
        return self._get_available_days('date')

    def get_data(self, start_date, end_date, metrics):
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
        es_query = es_query.filter('range', date={
            'gte': start_date + '||/d',
            'lte': end_date + '||/d',
            'format': 'yyyy-MM-dd',
            'time_zone': '+00:00'
        })

        return es_query
