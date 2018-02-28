# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .datafile import DataFile, get_timestamp

import csv
import io


class SpeedFile(DataFile):
    """ Class that represents a speed file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)

    def makeDocs(self):
        with io.open(self.datafile, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                path = self.getPath()
                timestamp = get_timestamp()
                merged = str(row['route'] + '-' + row['section'] + '-' + row['periodId'])
                yield {"_source": dict(timestamp=timestamp, path=path, merged=merged, **row)}

    def getHeader(self):
        return 'route|section|date|periodId|dayType|totalDistance|totalTime|speed|nObs|nInvalidObs'
