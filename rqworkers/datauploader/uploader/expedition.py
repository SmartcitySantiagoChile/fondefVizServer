# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .datafile import DataFile, get_timestamp

import csv
import io


class ExpeditionFile(DataFile):
    """ Class that represents an expedition file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)

    def makeDocs(self):
        with io.open(self.datafile, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                path = self.getPath()
                timestamp = get_timestamp()
                route = row['route']
                license_plate = row['licensePlate']
                expedition_start_time = row['expeditionStartTime']
                expedition_end_time = row['expeditionEndTime']
                fulfillment = row['fulfillment']
                period_id = row['periodId']
                yield {
                    "_source": {
                        "path": path,
                        "timestamp": timestamp,
                        "route": route,
                        "licensePlate": license_plate,
                        "expeditionStartTime": expedition_start_time,
                        "expeditionEndTime": expedition_end_time,
                        "fulfillment": fulfillment,
                        "periodId": period_id
                    }
                }

    def getHeader(self):
        return 'route|licensePlate|a|b|expeditionStartTime|expeditionEndTime|fulfillment|c|d|e|f|g|h|periodId'
