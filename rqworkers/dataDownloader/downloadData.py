# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch import Elasticsearch

import sys
sys.path.append('D:\\PycharmProjects\\fondefVizServer')

# from rqworkers.dataDownloader.downloader.odbyroute import OdByRouteFile
from rqworkers.dataDownloader.downloader.profile import ProfileDataByExpedition, ProfileDataByStop
# from rqworkers.dataDownloader.downloader.shape import ShapeFile
# from rqworkers.dataDownloader.downloader.speed import SpeedFile
# from rqworkers.dataDownloader.downloader.stop import StopFile
# from rqworkers.dataDownloader.downloader.trip import TripFile

from errors import UnrecognizedIndexNameError

import argparse


def download_file(es_instance, query, index_name, zip_file_path, chunk_size=5000, timeout=30):
    """ download file to elasticsearch """

    # Determine file type according to index name
    if index_name == 'odbyroute':
        data_to_download = OdByRouteFile()
    elif index_name == 'profile':
        data_to_download = ProfileDataByExpedition()
    elif index_name == 'shape':
        data_to_download = ShapeFile()
    elif index_name == 'speed':
        data_to_download = SpeedFile()
    elif index_name == 'stop':
        data_to_download = StopFile()
    elif index_name == 'trip':
        data_to_download = TripFile()
    else:
        raise UnrecognizedIndexNameError()

    # Load file to elasticsearch
    data_to_download.download(es_instance, query, index_name, zip_file_path, chunk_size, timeout)


def main():
    """
    This script will create an index on a existing elasticsearch instance and populate it using data from a given
    file. If an index with the same name already exists, it will use that index instead.
    """

    # Arguments and description
    parser = argparse.ArgumentParser(description='Download data from elasticsearch to file with csv format')

    parser.add_argument('query', help='dsl query')
    parser.add_argument('index', help='name of the index to use')
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

    print('downloading data from index \'{0}\' to file {1}'.format(index_name, csv_file))
    download_file(es, query, index_name, csv_file, chunk_size, timeout)


if __name__ == "__main__":
    main()
