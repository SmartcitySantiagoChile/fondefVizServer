# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
import django
import argparse
import json

# add path so we can use function through command line
new_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(new_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fondefVizServer.settings")
django.setup()

from elasticsearch import Elasticsearch

from rqworkers.dataDownloader.csvhelper.profile import ProfileByExpeditionData, ProfileDataByStop
from rqworkers.dataDownloader.csvhelper.odbyroute import OdByRouteData
from rqworkers.dataDownloader.csvhelper.speed import SpeedData
from rqworkers.dataDownloader.csvhelper.trip import TripData

from rqworkers.dataDownloader.errors import UnrecognizedDownloaderNameError

import rqworkers.dataDownloader.csvhelper.helper as csv_helper


def download_file(es_instance, query, downloader, zip_file_path):
    """ download file to elasticsearch """

    # Determine file type according to index name
    if downloader == csv_helper.OD_BY_ROUTE_DATA:
        data_to_download = OdByRouteData(query, es_instance)
    elif downloader == csv_helper.PROFILE_BY_EXPEDITION_DATA:
        data_to_download = ProfileByExpeditionData(query, es_instance)
    elif downloader == csv_helper.PROFILE_BY_STOP_DATA:
        data_to_download = ProfileDataByStop(query, es_instance)
    elif downloader == csv_helper.SPEED_MATRIX_DATA:
        data_to_download = SpeedData(query, es_instance)
    elif downloader == csv_helper.TRIP_DATA:
        data_to_download = TripData(query, es_instance)
    else:
        raise UnrecognizedDownloaderNameError()

    # Download data to file from elasticsearch
    data_to_download.build_file(zip_file_path)


def main():
    """
    This script will create an index on a existing elasticsearch instance and populate it using data from a given
    file. If an index with the same name already exists, it will use that index instead.
    """

    # Arguments and description
    parser = argparse.ArgumentParser(description='Download data from elasticsearch to file with csv format')

    parser.add_argument('query', help='dsl query')
    parser.add_argument('downloader',
                        help='you can choose: profile_by_expedition, profile_by_stop, od_by_route_data, trip_data, speed_matrix_data')
    parser.add_argument('file', help='data file path, e.g. /path/to/file.csvhelper')
    parser.add_argument('--host', default="127.0.0.1", help='elasticsearch host, default is "127.0.0.1"')
    parser.add_argument('--port', default=9200, help='elasticsearch port, default is 9200')
    args = parser.parse_args()

    # Get a client
    es = Elasticsearch(hosts=[{"host": args.host, "port": args.port}])

    # Give names to arguments
    query = args.query
    downloader = args.downloader
    csv_file = args.file

    query = json.loads(query.replace('\'', '"'))
    print('downloading data to file {1} with downloader \'{1}\''.format(csv_file, downloader))
    download_file(es, query, downloader, csv_file)


if __name__ == "__main__":
    main()
