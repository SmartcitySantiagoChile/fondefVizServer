# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rqworkers.dataDownloader.downloader.datadownloader import DataDownloader

from esapi.helper.stop import ESStopHelper


class StopFile(DataDownloader):
    """ Class that represents a stop file. """

    def __init__(self, es_client, es_query):
        DataDownloader.__init__(self, es_client, es_query, ESStopHelper().get_index_name())

        self.column_dict = [
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación'},
            {'es_name': 'points', 'csv_name': 'Latitud,Longitud'}
        ]
        self.translator = self.create_translator()

    def row_parser(self, row, path, timestamp):
        pass

    def make_docs(self):
        with self.get_file_object() as f:
            next(f)  # skip header
            delimiter = str('|')
            reader = csv.DictReader(f, delimiter=delimiter, fieldnames=self.fieldnames)

            # Group data using 'authRouteCode' as key
            for authUserOp, stops in groupby(reader,
                                             lambda r: (r['authRouteCode'], r['userRouteCode'], r['operator'])):
                # skip if authority operator code is an hyphen
                if authUserOp[0] == str('-'):
                    continue
                try:
                    path = self.basename
                    timestamp = get_timestamp()
                    date = self.name_to_date()
                    stops = [
                        {
                            'order': int(p['order']),
                            'longitude': float(p['longitude']),
                            'latitude': float(p['latitude']),
                            'authStopCode': p['authStopCode'],
                            'userStopCode': p['userStopCode'],
                            'stopName': p['stopName'].decode('latin-1'),
                        } for p in stops
                    ]
                    yield {
                        "_source": {
                            "path": path,
                            "timestamp": timestamp,
                            "startDate": date,
                            "authRouteCode": authUserOp[0],
                            "userRouteCode": authUserOp[1],
                            "operator": int(authUserOp[2]),
                            "stops": stops
                        }
                    }
                except ValueError:
                    traceback.print_exc()
