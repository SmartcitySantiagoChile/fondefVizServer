from rqworkers.dataUploader.uploader.datafile import DataFile


class OdByRouteFile(DataFile):
    """ Class that represents an odbyroute file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)
        self.fieldnames = ['date', 'dateType', 'authRouteCode', 'operator', 'userRouteCode', 'timePeriodInStopTime',
                           'startStopOrder', 'endStopOrder', 'authStartStopCode', 'authEndStopCode',
                           'userStartStopCode', 'userEndStopCode', 'startStopName', 'endStopName', 'startZone',
                           'endZone', 'tripNumber', 'tripWithoutLanding', 'expandedTripNumber']

    def row_parser(self, row, path, timestamp):
        return {
            "path": path,
            "timestamp": timestamp,
            "date": row['date'],
            "dateType": row['dateType'],
            "authRouteCode": row['authRouteCode'],
            "operator": int(row['operator']),
            "userRouteCode": row['userRouteCode'],
            "timePeriodInStopTime": row['timePeriodInStopTime'],
            "startStopOrder": int(row['startStopOrder']),
            "endStopOrder": int(row['endStopOrder']),
            "authStartStopCode": row['authStartStopCode'],
            "authEndStopCode": row['authEndStopCode'],
            "userStartStopCode": row['userStartStopCode'],
            "userEndStopCode": row['userEndStopCode'],
            "startStopName": row['startStopName'].decode('latin-1'),
            "endStopName": row['endStopName'].decode('latin-1'),
            "startZone": int(row['startZone']),
            "endZone": int(row['endZone']),
            "tripNumber": int(row['tripNumber']),
            "tripWithoutLanding": int(row['tripWithoutLanding']),
            "expandedTripNumber": float(row['expandedTripNumber'])
        }
