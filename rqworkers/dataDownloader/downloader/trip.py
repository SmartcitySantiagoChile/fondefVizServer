from rqworkers.dataUploader.uploader.datafile import DataFile


class TripFile(DataFile):
    """ Class that represents a trip file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)
        self.fieldnames = ['id', 'tipodia', 'factor_expansion', 'n_etapas', 'tviaje', 'distancia_eucl',
                           'distancia_ruta', 'tiempo_subida', 'tiempo_bajada', 'mediahora_subida', 'mediahora_bajada',
                           'periodo_subida', 'periodo_bajada', 'tipo_transporte_1', 'tipo_transporte_2',
                           'tipo_transporte_3', 'tipo_transporte_4', 'srv_1', 'srv_2', 'srv_3', 'srv_4',
                           'paradero_subida', 'paradero_bajada', 'comuna_subida', 'comuna_bajada', 'zona_subida',
                           'zona_bajada']

    def row_parser(self, row, path, timestamp):
        return {
            "path": path,
            "timestamp": timestamp,
            "id": int(row['id']),
            "tipodia": int(row['tipodia']),
            "factor_expansion": float(row['factor_expansion']),
            "n_etapas": int(row['n_etapas']),
            "tviaje": float(row['tviaje']),
            "distancia_eucl": float(row['distancia_eucl']),
            "distancia_ruta": float(row['distancia_ruta']),
            "tiempo_subida": row['tiempo_subida'],
            "tiempo_bajada": row['tiempo_bajada'],
            "mediahora_subida": int(row['mediahora_subida']),
            "mediahora_bajada": int(row['mediahora_bajada']),
            "periodo_subida": int(row['periodo_subida']),
            "periodo_bajada": int(row['periodo_bajada']),
            "tipo_transporte_1": int(row['tipo_transporte_1']),
            "tipo_transporte_2": int(row['tipo_transporte_2']),
            "tipo_transporte_3": int(row['tipo_transporte_3']),
            "tipo_transporte_4": int(row['tipo_transporte_4']),
            "srv_1": row['srv_1'],
            "srv_2": row['srv_2'],
            "srv_3": row['srv_3'],
            "srv_4": row['srv_4'],
            "paradero_subida": row['paradero_subida'],
            "paradero_bajada": row['paradero_bajada'],
            "comuna_subida": int(row['comuna_subida']),
            "comuna_bajada": int(row['comuna_bajada']),
            "zona_subida": int(row['zona_subida']),
            "zona_bajada": int(row['zona_bajada'])
        }
