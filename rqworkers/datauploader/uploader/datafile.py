# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch.helpers import parallel_bulk
from datetime import datetime
from subprocess import call

import csv
import io
import os
import re


class DataFile:
    def __init__(self, datafile):
        self.datafile = datafile
        self.mapping = self.getMapping()

    def getMapping(self):
        filename, file_extension = os.path.basename(self.datafile).split(".")
        current_dir = os.path.dirname(__file__)
        mapping_file = os.path.join(current_dir, '..', 'mappings', file_extension + '-template.json')
        return mapping_file

    def load(self, client, index_name, chunk_size, threads, timeout):
        # The file needs to have the right header
        self.fixHeader()
        # Create index with mapping. If it already exists, ignore this
        client.indices.create(index=index_name, ignore=400, body=open(self.mapping, 'r').read())
        # Send docs to elasticsearch
        for success, info in parallel_bulk(client, self.makeDocs(), thread_count=threads, chunk_size=chunk_size,
                                           request_timeout=timeout,
                                           index=index_name,
                                           doc_type='doc'):
            if not success: print('Doc failed', info)

    # Yield all fields in file + path and timestamp
    def makeDocs(self):
        with io.open(self.datafile, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                path = os.path.basename(self.datafile)
                timestamp = datetime.now()
                yield {"_source": dict(timestamp=timestamp, path=path, **row)}

    def getHeader(self):
        filename, extension = os.path.basename(self.datafile).split(".")
        return {
            'general': 'date|dayType|expeditionNumber|minExpeditionTime|maxExpeditionTime|averageExpeditionTime|licensePlateNumber|GPSPointsNumber|averageTimeBetweenGPSPoints|GPSNumberWithRoute|GPSNumberWithoutRoute|transactionNumber|transactionOnBusNumber|transactionOnMetroNumber|transactionOnTrainNumber|transactionOnBusStation|smartcardNumber|transactionWithRoute|transactionWithoutRoute|stagesWithBusAlighting|stagesWithMetroAlighting|stagesWithTrainAlighting|stagesWithBusStationAlighting|tripNumber|completeTripNumber|tripsWithOneStage|tripsWithTwoStages|tripsWithThreeStages|tripsWithFourStages|tripsWithFiveOrMoreStages|tripsWithOnlyMetro|tripsThatUseMetro|tripsWithoutLastAlighting|validTripNumber|averageTimeOfTrips|averageDistanceOfTrips|averageVelocityOfTrips|tripNumberInMorningRushHour|averageTimeInMorningRushTrips|averageDistanceInMorningRushTrips|averageVelocityInMorningRushTrips|tripNumberInAfternoonRushHour|averageTimeInAfternoonRushTrips|averageDistanceInAfternoonRushTrips|averageVelocityInAfternoonRushTrips',
            'travel': 'id|tipodia|factor_expansion|n_etapas|tviaje|distancia_eucl|distancia_ruta|tiempo_subida|tiempo_bajada|mediahora_subida|mediahora_bajada|periodo_subida|periodo_bajada|tipo_transporte_1|tipo_transporte_2|tipo_transporte_3|tipo_transporte_4|srv_1|srv_2|srv_3|srv_4|paradero_subida|paradero_bajada|comuna_subida|comuna_bajada|zona_subida|zona_bajada',
            'od': 'date|dateType|authRouteCode|operator|userRouteCode|timePeriodInStopTime|startStopOrder|endStopOrder|authStartStopCode|authEndStopCode|userStartStopCode|userEndStopCode|startStopName|endStopName|startZone|endZone|tripNumber|tripWithoutLanding|expandedTripNumber',
        }[extension]

    def headerIsOK(self):
        # Read first line
        with io.open(self.datafile, 'r', encoding='latin-1') as f:
            header = f.readline().rstrip('\n')
        # If the header is already the one we want
        if header == self.getHeader():
            return True
        else:
            return False

    def hasHeader(self):
        # Read first line
        with io.open(self.datafile, 'r', encoding='latin-1') as f:
            header = f.readline().rstrip('\n')
        # Check it only contains letters, spaces, |'s and #'s
        search = re.compile(r'[^a-zA-Z|# .]').search
        return not bool(search(header))

    def removeHeader(self):
        # Remove first line of the file
        call(["sed", "-i", '1d', self.datafile])

    def addHeader(self):
        # Put this on the first line
        call(["sed", "-i", '1i ' + self.getHeader(), self.datafile])

    def fixHeader(self):
        # Check if the file has a header
        if self.hasHeader():
            if self.headerIsOK():
                pass
            else:
                self.removeHeader()
                self.addHeader()
        else:
            self.addHeader()

    def getPath(self):
        return os.path.basename(self.datafile)


def get_timestamp():
    return datetime.utcnow()


def name_to_date(filename):
    start_date = datetime.strptime(filename, '%Y-%m-%d').isoformat() + '.000Z'  # Python doesn't support military Z.
    return start_date
