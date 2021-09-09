import argparse
import json
import os
import sys

import django

# add path so we can use function through command line
new_path = os.path.join(os.path.dirname(__file__), '../rqworkers', '..')
sys.path.append(new_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fondefVizServer.settings")
django.setup()

from elasticsearch import Elasticsearch

from dataDownloader.csvhelper.profile import ProfileByExpeditionData, ProfileDataByStop
from dataDownloader.csvhelper.odbyroute import OdByRouteData
from dataDownloader.csvhelper.speed import SpeedDataWithFormattedShape
from dataDownloader.csvhelper.trip import TripData, PostProductTripTripBetweenZonesData, \
    PostProductTripBoardingAndAlightingData, PostProductTripBoardingAndAlightingWithoutServiceData
from dataDownloader.csvhelper.stage import PostProductStageTransferData, PostProductStageTransferAggregatedData, PostProductStageTransactionsByOperatorData
from dataDownloader.csvhelper.paymentfactor import PaymentFactorData
from dataDownloader.csvhelper.bip import BipData

from dataDownloader.errors import UnrecognizedDownloaderNameError

import dataDownloader.csvhelper.helper as csv_helper


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
        data_to_download = SpeedDataWithFormattedShape(query, es_instance)
    elif downloader == csv_helper.TRIP_DATA:
        data_to_download = TripData(query, es_instance)
    elif downloader == csv_helper.PAYMENT_FACTOR_DATA:
        data_to_download = PaymentFactorData(query, es_instance)
    elif downloader == csv_helper.BIP_DATA:
        data_to_download = BipData(query, es_instance)
    elif downloader == csv_helper.POST_PRODUCTS_STAGE_TRANSFERS_DATA:
        data_to_download = PostProductStageTransferData(query, es_instance)
    elif downloader == csv_helper.POST_PRODUCTS_STAGE_TRANSFERS_AGGREGATED_DATA:
        data_to_download = PostProductStageTransferAggregatedData(query, es_instance)
    elif downloader == csv_helper.POST_PRODUCTS_TRIP_TRIP_BETWEEN_ZONES_DATA:
        data_to_download = PostProductTripTripBetweenZonesData(query, es_instance)
    elif downloader == csv_helper.POST_PRODUCTS_TRIP_BOARDING_AND_ALIGHTING_DATA:
        data_to_download = PostProductTripBoardingAndAlightingData(query, es_instance)
    elif downloader == csv_helper.POST_PRODUCTS_TRIP_BOARDING_AND_ALIGHTING_WITHOUT_SERVICE_DATA:
        data_to_download = PostProductTripBoardingAndAlightingWithoutServiceData(query, es_instance)
    elif downloader == csv_helper.POST_PRODUCTS_STAGE_TRANSACTIONS_BY_OPERATOR_DATA:
        data_to_download = PostProductStageTransactionsByOperatorData(query, es_instance)
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
    print(('downloading data to file {1} with downloader \'{1}\''.format(csv_file, downloader)))
    download_file(es, query, downloader, csv_file)


if __name__ == "__main__":
    main()
