# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import groupby

from .datafile import DataFile, get_timestamp, name_to_date

import os
import csv
import io


class StopFile(DataFile):
    """ Class that represents a stop file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)

    def makeDocs(self):
        # Get filename and extension
        filename, file_extension = os.path.basename(self.datafile).split(".")
        with io.open(self.datafile, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter='|')
            # Group data using 'authRouteCode' as key
            for authUserOp, stops in groupby(reader, lambda r: (r['authRouteCode'], r['userRouteCode'], r['operator'])):
                stops = list(stops)
                path = self.getPath()
                timestamp = get_timestamp()
                date = name_to_date(filename)
                stops = [
                    {
                        'order': p['order'],
                        'longitude': p['longitude'],
                        'latitude': p['latitude'],
                        'authStopCode': p['authStopCode'],
                        'userStopCode': p['userStopCode'],
                        'stopName': p['stopName']
                    } for p in stops
                ]
                yield {
                    "_source": {
                        "path": path,
                        "timestamp": timestamp,
                        "date": date,
                        "authRouteCode": authUserOp[0],
                        "userRouteCode": authUserOp[1],
                        "operator": authUserOp[2],
                        "stops": stops
                    }
                }

    def getHeader(self):
        return 'authRouteCode|userRouteCode|operator|order|authStopCode|userStopCode|stopName|latitude|longitude'


'''    def makeDocs(self):
        # Get filename and extension
        filename, file_extension = os.path.basename(self.datafile).split(".")
        with open(self.datafile, "r") as f:
            reader = csv.DictReader(f, delimiter='|')
            # Group data using 'route' as key
            for route, points in groupby(reader, lambda p: p['route']):
                points = list(points)
                startDate = nameToDate(filename)
                path = self.getPath()
                timestamp = getTimeStamp()
                points = [
                    {
                        'segmentStart': p['segmentStart'],
                        'longitude': p['longitude'],
                        'latitude': p['latitude']
                    } for p in points
                ]
                yield {
                    "_source": {
                        "path": path,
                        "timestamp": timestamp,
                        "route": route,
                        "startDate": startDate,
                        "points": points
                    }
                }
'''
