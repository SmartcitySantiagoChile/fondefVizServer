# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import groupby

from .datafile import DataFile, get_timestamp, name_to_date

import csv
import io
import os


class ShapeFile(DataFile):
    """ Class that represents a shape file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)

    def makeDocs(self):
        # Get filename and extension
        filename, file_extension = os.path.basename(self.datafile).split(".")
        with io.open(self.datafile, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter='|')
            # Group data using 'route' as key
            for route, points in groupby(reader, lambda point: point['route']):
                points = list(points)
                start_date = name_to_date(filename)
                path = self.getPath()
                timestamp = get_timestamp()
                points = [{'segmentStart': p['segmentStart'], 'longitude': p['longitude'], 'latitude': p['latitude']}
                          for p in points]
                yield {
                    "_source": {
                        "path": path,
                        "timestamp": timestamp,
                        "route": route,
                        "startDate": start_date,
                        "points": points
                    }
                }

    def getHeader(self):
        return 'route|segmentStart|latitude|longitude'
