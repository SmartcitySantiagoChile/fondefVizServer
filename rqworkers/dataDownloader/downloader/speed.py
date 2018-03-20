# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataUploader.uploader.datafile import DataFile


class SpeedFile(DataFile):
    """ Class that represents a speed file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)
        self.fieldnames = ['route', 'section', 'date', 'periodId', 'dayType', 'totalDistance',
                           'totalTime', 'speed', 'nObs', 'nInvalidObs']

    def row_parser(self, row, path, timestamp):
        merged = str(row['route'] + '-' + row['section'] + '-' + row['periodId'])
        return {
            "path": path,
            "timestamp": timestamp,
            "merged": merged,
            "route": row['route'],
            "section": int(row['section']),
            "date": row['date'],
            "periodId": int(row['periodId']),
            "dayType": int(row['dayType']),
            "totalDistance": float(row['totalDistance']),
            "totalTime": float(row['totalTime']),
            "speed": float(row['speed']),
            "nObs": int(row['nObs']),
            "nInvalidObs": int(row['nInvalidObs'])
        }
