from esapi.helper.basehelper import ElasticSearchHelper


class ESResumeStatisticHelper(ElasticSearchHelper):

    def __init__(self):
        index_name = "general"
        super(ESResumeStatisticHelper, self).__init__(index_name)

    def ask_for_available_days(self):
        """ get unique list for: timePeriodInStartTime, dayType, expeditionStartTime """

        searches = {
            "days": self.get_histogram_query("date", interval="day", format="yyy-MM-dd")
        }
        result = self.make_multisearch_query_for_aggs(searches)["days"]

        return result

    def ask_for_data(self, start_date, end_date, metrics):

        if len(metrics) == 0:
            metrics = ["transactionWithoutRoute", "transactionWithRoute", "transactionNumber",
                       "transactionOnTrainNumber", "transactionOnMetroNumber", "transactionOnBusNumber",
                       "transactionOnBusStation", "averageVelocityInAfternoonRushTrips",
                       "averageTimeInAfternoonRushTrips", "averageDistanceInAfternoonRushTrips",
                       "tripNumberInAfternoonRushHour", "averageVelocityInMorningRushTrips",
                       "averageTimeInMorningRushTrips", "averageDistanceInMorningRushTrips",
                       "tripNumberInMorningRushHour", "licensePlateNumber", "GPSPointsNumber", "GPSNumberWithRoute",
                       "GPSNumberWithoutRoute", "expeditionNumber", "maxExpeditionTime", "minExpeditionTime",
                       "averageExpeditionTime", "smartcardNumber", "tripNumber", "averageTimeOfTrips",
                       "averageVelocityOfTrips", "averageTimeBetweenGPSPoints", "averageDistanceOfTrips",
                       "tripsThatUseMetro", "completeTripNumber", "stagesWithBusStationAlighting",
                       "tripsWithoutLastAlighting", "validTripNumber", "tripsWithOneStage", "tripsWithTwoStages",
                       "tripsWithThreeStages", "tripsWithFourStages", "tripsWithFiveOrMoreStages", "tripsWithOnlyMetro",
                       "stagesWithBusAlighting", "stagesWithTrainAlighting", "stagesWithMetroAlighting", "dayType"
                       ]

        es_query = self.get_base_query()
        es_query = es_query.source(["date"] + metrics)
        es_query = es_query.filter("range", date={
            "gte": start_date + "||/d",
            "lte": end_date + "||/d",
            "format": "yyyy-MM-dd",
            "time_zone": "+00:00"
        })

        return es_query.scan()
