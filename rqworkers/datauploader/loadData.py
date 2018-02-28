# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from elasticsearch import Elasticsearch

from .uploader.datafile import DataFile
from .uploader.expedition import ExpeditionFile
from .uploader.profile import ProfileFile
from .uploader.shape import ShapeFile
from .uploader.speed import SpeedFile
from .uploader.stop import StopFile

import argparse
import os


def get_extension(datafile):
    """ Get filename and extension """
    filename, file_extension = os.path.basename(datafile).split(".")
    return file_extension


def upload_file(es_instance, datafile, index_name=None, chunk_size=5000, threads=4, timeout=30):
    """ upload file to elasticsearch """

    # Get file extension
    file_extension = get_extension(datafile)

    # If no index name was supplied, index name is the same as file extension
    if index_name is None:
        index_name = file_extension

    # Determine file type according to the extension
    if file_extension == 'shape':
        file_to_load = ShapeFile(datafile)
    elif file_extension == 'speed':
        file_to_load = SpeedFile(datafile)
    elif file_extension == 'expedition':
        file_to_load = ExpeditionFile(datafile)
    elif file_extension == 'profile':
        file_to_load = ProfileFile(datafile)
    elif file_extension == 'stop':
        file_to_load = StopFile(datafile)
    else:
        file_to_load = DataFile(datafile)

    # Load file to elasticsearch
    file_to_load.load(es_instance, index_name, chunk_size, threads, timeout)


def main():
    """
    This script will create an index on a existing elasticsearch instance and populate it using data from a given
    file. If an index with the same name already exists, it will use that index instead.
    """

    # Arguments and description
    parser = argparse.ArgumentParser(description='Add documents from a file to an elasticsearch index.')

    parser.add_argument('file', help='data file path, e.g. /path/to/file')
    parser.add_argument('--host', default="127.0.0.1", help='elasticsearch host, default is "127.0.0.1"')
    parser.add_argument('--port', default=9200, help='port, default is 9200')
    parser.add_argument('--index', help='name of the index to create/use')
    parser.add_argument('--chunk', default=5000, type=int, help='number of docs to send in one chunk, default is 5000')
    parser.add_argument('--threads', default=4, type=int, help='number of threads to use, default is 4')
    parser.add_argument('--timeout', default=30, type=int,
                        help='explicit timeout for each call, default is 30 (seconds)')
    args = parser.parse_args()

    # Get a client
    es = Elasticsearch(hosts=[{"host": args.host, "port": args.port}])

    # Give names to arguments
    index_name = args.index
    datafile = args.file
    chunk_size = args.chunk
    threads = args.threads
    timeout = args.timeout

    upload_file(es, datafile, index_name, chunk_size, threads, timeout)


if __name__ == "__main__":
    main()
