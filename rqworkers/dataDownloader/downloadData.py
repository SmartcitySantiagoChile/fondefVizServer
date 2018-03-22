# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
import django
import argparse
import json

sys.path.append('C:\\Users\\cephei\\PycharmProjects\\fondefVizServer')
sys.path.append('D:\\PycharmProjects\\fondefVizServer')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fondefVizServer.settings")
django.setup()

from elasticsearch import Elasticsearch

from rqworkers.dataDownloader.downloader.datadownloader import DataDownloader
from rqworkers.dataDownloader.downloader.odbyroute import OdByRouteFile
from rqworkers.dataDownloader.downloader.profile import ProfileDataByExpedition, ProfileDataByStop
from rqworkers.dataDownloader.downloader.shape import ShapeFile
from rqworkers.dataDownloader.downloader.speed import SpeedFile
from rqworkers.dataDownloader.downloader.stop import StopFile
from rqworkers.dataDownloader.downloader.trip import TripFile

from rqworkers.dataDownloader.errors import UnrecognizedDownloaderNameError


def download_file(es_instance, query, downloader, zip_file_path, chunk_size=5000, timeout=30):
    """ download file to elasticsearch """

    # Determine file type according to index name
    if downloader == DataDownloader.OD_BY_ROUTE_DATA:
        data_to_download = OdByRouteFile(es_instance, query)
    elif downloader == DataDownloader.PROFILE_BY_EXPEDITION_DATA:
        data_to_download = ProfileDataByExpedition(es_instance, query)
    elif downloader == DataDownloader.PROFILE_BY_STOP_DATA:
        data_to_download = ProfileDataByStop(es_instance, query)
    elif downloader == DataDownloader.SHAPE_DATA:
        data_to_download = ShapeFile(es_instance, query)
    elif downloader == DataDownloader.SPEED_MATRIX_DATA:
        data_to_download = SpeedFile(es_instance, query)
    elif downloader == DataDownloader.STOP_DATA:
        data_to_download = StopFile(es_instance, query)
    elif downloader == DataDownloader.TRIP_DATA:
        data_to_download = TripFile(es_instance, query)
    else:
        raise UnrecognizedDownloaderNameError()

    # Download data to file from elasticsearch
    data_to_download.download(zip_file_path, chunk_size, timeout)


def main():
    """
    This script will create an index on a existing elasticsearch instance and populate it using data from a given
    file. If an index with the same name already exists, it will use that index instead.
    """

    # Arguments and description
    parser = argparse.ArgumentParser(description='Download data from elasticsearch to file with csv format')

    parser.add_argument('query', help='dsl query')
    parser.add_argument('downloader', help='you can choose: profile_by_expedition, profile_by_stop, od_by_route_data, shape_data, stop_data, speed_matrix_data')
    parser.add_argument('file', help='data file path, e.g. /path/to/file.csv')
    parser.add_argument('--host', default="127.0.0.1", help='elasticsearch host, default is "127.0.0.1"')
    parser.add_argument('--port', default=9200, help='port, default is 9200')
    parser.add_argument('--chunk', default=5000, type=int, help='number of docs to send in one chunk, default is 5000')
    parser.add_argument('--timeout', default=30, type=int,
                        help='explicit timeout for each call, default is 30 (seconds)')
    args = parser.parse_args()

    # Get a client
    es = Elasticsearch(hosts=[{"host": args.host, "port": args.port}])

    # Give names to arguments
    query = args.query
    index_name = args.index
    csv_file = args.file
    chunk_size = args.chunk
    timeout = args.timeout

    query = json.loads(query.replace('\'', '"'))
    print('downloading data from index \'{0}\' to file {1}'.format(index_name, csv_file))
    download_file(es, query, index_name, csv_file, chunk_size, timeout)


if __name__ == "__main__":
    main()
