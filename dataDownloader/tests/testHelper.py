import filecmp
import os
import zipfile
from unittest import mock

from django.test import TestCase, override_settings

from dataDownloader.csvhelper import helper


class TestZipManager(TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'files', 'test.zip')
        self.zip_manager = helper.ZipManager(self.path)

    def test_build_readme(self):
        self.zip_manager.build_readme('title', 'file_description', 'data_filter', 'field_explanation')
        self.zip_manager.close()
        self.assertTrue(zipfile.is_zipfile(self.path))
        zip_file_obj = zipfile.ZipFile(self.path)
        file_name = zip_file_obj.namelist()[0]
        zip_file_obj.extract(file_name, os.path.join(os.path.dirname(__file__), 'files'))
        path_test = os.path.join(os.path.dirname(__file__), 'files', 'Léeme.txt')
        self.assertTrue(filecmp.cmp(os.path.join(os.path.dirname(__file__), 'files', 'Léeme-test.txt'),
                                    path_test))
        zip_file_obj.close()
        os.remove(path_test)
        os.remove(self.path)


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestCSVHelper(TestCase):
    def test_get_column_dict(self):
        self.assertRaises(NotImplementedError, helper.CSVHelper, None, None, None)


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestProfileCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.ProfileCSVHelper(None, {})

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Perfil.csv")

    def test_get_column_dict(self):
        expected = [{'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
                    {'es_name': 'route', 'csv_name': 'Servicio_transantiago',
                     'definition': 'Código de transantiago del servicio'},
                    {'es_name': 'userRoute', 'csv_name': 'Servicio_usuario',
                     'definition': 'Código de usuario del servicio (ejemplo: 506)'},
                    {'es_name': 'licensePlate', 'csv_name': 'Patente',
                     'definition': 'Patente de la máquina que realizó la expedición'},
                    {'es_name': 'authStopCode', 'csv_name': 'Código_parada_transantiago',
                     'definition': 'Código de transantiago de la parada por la que pasó el servicio'},
                    {'es_name': 'userStopCode', 'csv_name': 'Código_parada_usuario',
                     'definition': 'Código de usuario de la parada por la que pasó el servicio (ejemplo: PA433)'},
                    {'es_name': 'userStopName', 'csv_name': 'Nombre_parada',
                     'definition': 'Nombre de la parada por la que pasó el servicio'},
                    {'es_name': 'expeditionStartTime', 'csv_name': 'Hora_inicio_expedición',
                     'definition': 'Fecha y hora de inicio de la expedición'},
                    {'es_name': 'expeditionEndTime', 'csv_name': 'Hora_fin_expedición',
                     'definition': 'Fecha y hora de fin de la expedición'},
                    {'es_name': 'fulfillment', 'csv_name': 'Cumplimiento',
                     'definition': 'La expedición cumple la condición de cruzar por los puntos de control de inicio y fin de ruta indicado en el reporte 1.96'},
                    {'es_name': 'expeditionStopOrder', 'csv_name': 'Secuencia_parada',
                     'definition': 'Posición de la parada dentro de la secuencia de paradas asociada al servicio'},
                    {'es_name': 'expeditionDayId', 'csv_name': 'Identificador_expedición_día',
                     'definition': 'identificador de la expedición, es único dentro del día'},
                    {'es_name': 'stopDistanceFromPathStart', 'csv_name': 'Distancia_parada_desde_inicio_ruta',
                     'definition': 'Distancia en metros entre el inicio de la ruta del servicio y la parada, considera la geometría de la ruta (no es euclidiana)'},
                    {'es_name': 'expeditionStopTime', 'csv_name': 'Hora_en_parada',
                     'definition': 'Fecha y hora en que la máquina pasó por la parada'},
                    {'es_name': 'timePeriodInStartTime', 'csv_name': 'Periodo_transantiago_inicio_expedicion',
                     'definition': 'Período transantiago en que inició la expedición'},
                    {'es_name': 'timePeriodInStopTime', 'csv_name': 'Periodo_transantiago_parada_expedición',
                     'definition': 'Período transantiago en que el bus cruza la parada'},
                    {'es_name': 'dayType', 'csv_name': 'Tipo_dia',
                     'definition': 'Tipo de día considerado por adatrap al momento de realizar el procesamiento de los datos'},
                    {'es_name': 'busStation', 'csv_name': 'Zona_paga',
                     'definition': 'Indica si la parada es zona paga (1: es zona paga, 0: no es zona paga)'},
                    {'es_name': 'transactions', 'csv_name': 'Número_transacciones_en_parada',
                     'definition': 'Número de transacciones realizadas en el paradero'},
                    {'es_name': 'halfHourInStartTime', 'csv_name': 'Media_hora_de_inicio_expedición',
                     'definition': 'Indica el período de media hora que la expedición inicio el recorrido (ejemplo: 16:00:00)'},
                    {'es_name': 'halfHourInStopTime', 'csv_name': 'Media_hora_en_parada',
                     'definition': 'Indica el período de media hora que la expedición pasó por la parada (ejemplo: 16:00:00)'},
                    {'es_name': 'notValid', 'csv_name': 'Expedición_inválida',
                     'definition': 'Indica si la expedición contiene alguno de los siguientes problemas -> porcentaje de paraderos con carga menor a -1 es superior al 1% o porcentaje de paraderos con carga mayor al 1% sobre la capacidad del bus es superior al 1%'},
                    {'es_name': 'expandedBoarding', 'csv_name': 'Subidas_expandidas',
                     'definition': 'Número de personas que subieron al bus en la parada, la expansión se realiza por período-servicio-sentido'},
                    {'es_name': 'expandedAlighting', 'csv_name': 'Bajadas_expandidas',
                     'definition': 'Número de personas que bajaron del bus en la parada, la expansión se realiza por período-servicio-sentido'},
                    {'es_name': 'loadProfile', 'csv_name': 'Perfil_carga_al_llegar',
                     'definition': 'Número de personas arriba del bus al llegar a la parada'},
                    {'es_name': 'busCapacity', 'csv_name': 'Capacidad_bus',
                     'definition': 'Número máximo de personas que pueden estar dentro del bus'},
                    {'es_name': 'expandedEvasionBoarding', 'csv_name': 'Subidas_evadidas',
                     'definition': 'Número de personas que subieron al bus y no pagaron su pasaje.'},
                    {'es_name': 'expandedEvasionAlighting', 'csv_name': 'Bajadas_evadidas',
                     'definition': 'Número de personas que bajaron del bus en la parada y no pagaron su pasaje.'},
                    {'es_name': 'expandedBoardingPlusExpandedEvasionBoarding', 'csv_name': 'Subidas_corregidas',
                     'definition': 'Número total de personas que subieron al bus incluyendo quienes no pagaron su pasaje.'},
                    {'es_name': 'expandedAlightingPlusExpandedEvasionAlighting', 'csv_name': 'Bajadas_corregidas',
                     'definition': 'Número total de personas que bajaron del bus en la parada incluyendo quienes no pagaron su pasaje.'},
                    {'es_name': 'loadProfileWithEvasion', 'csv_name': 'Carga_corregida',
                     'definition': 'Número de personas arriba del bus al llegar a la parada incluyendo quienes no pagaron su pasaje.'},
                    {'es_name': 'boardingWithAlighting', 'csv_name': 'Subidas_con_bajada',
                     'definition': 'Número de personas que subieron y tienen bajada estimada por ADATRAP.'},
                    {'es_name': 'evasionPercent', 'csv_name': '%evasión',
                     'definition': 'Porcentaje de evasión aplicado a las transacciones de la parada-expedición.'},
                    {'es_name': 'evasionType', 'csv_name': 'tipo_evasion',
                     'definition': 'pueden ser tres casos: 0, 1, 2, -1. El primero (0) indica que se usó una evasión a nivel de zonificación 777, el segundo valor (1) indica que se usó un valor de evasión a nivel de parada, y el tercer valor (2) indica que no se encontró un valor para el calculo de evasión. Existe un cuarto valor (-1) que indica que hubo un error con la información de evasión.'},
                    {'es_name': 'uniformDistributionMethod', 'csv_name': 'uniforme',
                     'definition': 'método de distribución uniforme para casos donde no es posible estimar bajada, "0" indica que se usó una distribución uniforme y el valor "1" significa que no se usó distribución uniforme.'},
                    {'es_name': 'passengerPerKmSection', 'csv_name': 'Pax-km_tramo',
                     'definition': 'Carga X distancia entre parada anterior y la del registro'},
                    {'es_name': 'passengerWithEvasionPerKmSection', 'csv_name': 'Pax-km_corregido_tramo',
                     'definition': 'Carga corregida X distancia entre parada anterior y la del registro'},
                    {'es_name': 'capacityPerKmSection', 'csv_name': 'Plazas-km_tramo',
                     'definition': 'Plazas de bus X distancia entre parada anterior y la del registro'},
                    ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Perfil.csv: archivo de perfiles de carga, cada fila representa el cruce de una expedición por una parada de su secuencia de parada.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestSpeedCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.SpeedCSVHelper(None, {})

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Velocidad_tramos_500m.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código transantiago del servicio'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario', 'definition': 'Código usuario del servicio'},
            {'es_name': 'section', 'csv_name': 'Identificador_tramo',
             'definition': 'Identificador del tramo de 500 metros (ejemplo: tramo 3 corresponde a la sección [1.500, 2.000] de la ruta del servicio)'},
            {'es_name': 'date', 'csv_name': 'Fecha_de_medición', 'definition': 'Fecha de la medición'},
            {'es_name': 'periodId', 'csv_name': 'Período_de_medición',
             'definition': 'Período de media hora de la medición'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día en que se realizó la medicion'},
            {'es_name': 'totalDistance', 'csv_name': 'Distancia_total',
             'definition': 'Distancia recorrida por las expediciones que cruzaron en el tramo en el período de medición'},
            {'es_name': 'totalTime', 'csv_name': 'Tiempo_total',
             'definition': 'Tiempo usado por las expediciones que cruzaron el tramo en el período de medición'},
            {'es_name': 'speed', 'csv_name': 'Velocidad_m/s', 'definition': 'Velocidad del tramo, período'},
            {'es_name': 'nObs', 'csv_name': 'Número_observaciones',
             'definition': 'Número de puntos gps utilizados para realizar el cálculo de la velocidad'},
            {'es_name': 'nInvalidObs', 'csv_name': 'Número_observaciones_inválidas',
             'definition': 'Número de observaciones no usadas'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Velocidad_tramos_500m.csv: Cada línea representa la medición de la velocidad para un servicio cada 500 metros en tramos horarios de media hora.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestODByRouteCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.ODByRouteCSVHelper(None, {})

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Matriz_etapas_por_servicio.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'date', 'csv_name': 'Fecha', 'definition': 'Día en que inició la etapa'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día en que inició la etapa'},
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario', 'definition': 'Código usuario del servicio'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código transantiago del servicio'},
            {'es_name': 'timePeriodInStopTime', 'csv_name': 'Período_transantiago_subida',
             'definition': 'Período transantiago en que la expedición pasó por la parada'},
            {'es_name': 'startStopOrder', 'csv_name': 'Posición_parada_en_ruta_subida',
             'definition': 'Posición de la parada de subida en la ruta del servicio'},
            {'es_name': 'endStopOrder', 'csv_name': 'Posición_parada_en_ruta_bajada',
             'definition': 'Posición de la parada de bajada en la ruta del servicio'},
            {'es_name': 'authStartStopCode', 'csv_name': 'Código_transantiago_parada_subida',
             'definition': 'Código transantiago de la parada de subida'},
            {'es_name': 'authEndStopCode', 'csv_name': 'Código_transantiago_parada_bajada',
             'definition': 'Código transantiago de la parada de bajada'},
            {'es_name': 'userStartStopCode', 'csv_name': 'Código_usuario_parada_subida',
             'definition': 'Código usuario de la parada de subida'},
            {'es_name': 'userEndStopCode', 'csv_name': 'Código_usuario_parada_bajada',
             'definition': 'Código usuario de la parada de bajada'},
            {'es_name': 'startStopName', 'csv_name': 'Nombre_parada_subida',
             'definition': 'Nombre de la parada de subida'},
            {'es_name': 'endStopName', 'csv_name': 'Nombre_parada_subida',
             'definition': 'Nombre de la parada de bajada'},
            {'es_name': 'startZone', 'csv_name': 'Zona_777_subida',
             'definition': 'Zona 777 asociada a la parada de subida'},
            {'es_name': 'endZone', 'csv_name': 'Zona_777_bajada',
             'definition': 'Zona 777 asociada a la parada de bajada'},
            {'es_name': 'tripNumber', 'csv_name': 'Número_etapas',
             'definition': 'Número de usuarios que realizó la etapa'},
            {'es_name': 'tripWithoutLanding', 'csv_name': 'Número_etapas_sin_bajada',
             'definition': 'Número de etapas sin bajada'},
            {'es_name': 'expandedTripNumber', 'csv_name': 'Número_etapas_expandido',
             'definition': 'Número de etapas expandido'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Matriz_etapas_por_servicio.csv: Cada línea representa la cantidad de etapas realizadas entre dos paradas en un período transantiago.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestTripCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.TripCSVHelper(None, {})

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Viajes.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'tipodia', 'csv_name': 'Tipo_día', 'definition': 'tipo de día en el que inició el viaje'},
            {'es_name': 'factor_expansion', 'csv_name': 'Factor_expansion',
             'definition': 'Factor de expansión asociado al viaje'},
            {'es_name': 'n_etapas', 'csv_name': 'Número_etapas',
             'definition': 'Número de etapas que constituyen el viaje'},
            {'es_name': 'tviaje', 'csv_name': 'Tiempo_viaje', 'definition': 'Duración del viaje en segundos'},
            {'es_name': 'distancia_eucl', 'csv_name': 'Distancia_euclidiana',
             'definition': 'Distancia euclidiana del viaje'},
            {'es_name': 'distancia_ruta', 'csv_name': 'Distancia_considerando_ruta',
             'definition': 'distancia considerando la ruta de los modos utilizados durante el viaje'},
            {'es_name': 'tiempo_subida', 'csv_name': 'Tiempo_subida',
             'definition': 'Fecha y hora en que se inició el viaje'},
            {'es_name': 'tiempo_bajada', 'csv_name': 'Tiempo_bajada',
             'definition': 'Fecha y hora en que terminó el viaje'},
            {'es_name': 'mediahora_subida', 'csv_name': 'Media_hora_subida',
             'definition': 'Tramo de media hora en que inició el viaje'},
            {'es_name': 'mediahora_bajada', 'csv_name': 'Media_hora_bajada',
             'definition': 'Tramo de media hora en que finalizó el viaje'},
            {'es_name': 'periodo_subida', 'csv_name': 'Periodo_transantiago_subida',
             'definition': 'Período transantiago en que inició el viaje'},
            {'es_name': 'periodo_bajada', 'csv_name': 'Período_transantiago_bajada',
             'definition': 'Período transantiago en que finalizó el viaje'},
            {'es_name': 'tipo_transporte_1', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 1'},
            {'es_name': 'tipo_transporte_2', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 2'},
            {'es_name': 'tipo_transporte_3', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 3'},
            {'es_name': 'tipo_transporte_4', 'csv_name': 'Tipo_transporte_etapa_1',
             'definition': 'Modo de transporte utilizado en la etapa 4'},
            {'es_name': 'srv_1', 'csv_name': 'Servicio_etapa_1', 'definition': 'Servicio utilizado en la etapa 1'},
            {'es_name': 'srv_2', 'csv_name': 'Servicio_etapa_2', 'definition': 'Servicio utilizado en la etapa 2'},
            {'es_name': 'srv_3', 'csv_name': 'Servicio_etapa_3', 'definition': 'Servicio utilizado en la etapa 3'},
            {'es_name': 'srv_4', 'csv_name': 'Servicio_etapa_4', 'definition': 'Servicio utilizado en la etapa 4'},
            {'es_name': 'paradero_subida', 'csv_name': 'Parada_subida',
             'definition': 'Código transantiago de la parada donde inició el viaje'},
            {'es_name': 'paradero_bajada', 'csv_name': 'Parada_bajada',
             'definition': 'Código transantiago de la parada donde finalizó el viaje'},
            {'es_name': 'comuna_subida', 'csv_name': 'Comuna_subida',
             'definition': 'Comuna asociada a la parada de subida de la primera etapa del viaje'},
            {'es_name': 'comuna_bajada', 'csv_name': 'Comuna_bajada',
             'definition': 'Comuna asociada a la parada de bajada de la última etapa del viaje'},
            {'es_name': 'zona_subida', 'csv_name': 'Zona_777_subida',
             'definition': 'Zona 777 asociada a la subida de la etapa 1 del viaje'},
            {'es_name': 'zona_bajada', 'csv_name': 'Zona_777_bajada',
             'definition': 'Zona 777 asociada a la bajada de la última etapa del viaje'},
            {'es_name': 'modos', 'csv_name': 'Modo_viajes',
             'definition': 'Modos de transporte utilizados en el viaje (resumen)'},
            {'es_name': 'zona_subida_1', 'csv_name': 'Zona_subidad_etapa_1',
             'definition': 'Zona 777 asociada a la subida de la etapa 1'},
            {'es_name': 'zona_bajada_1', 'csv_name': 'Zona_bajada_etapa_1',
             'definition': 'Zona 777 asociada a la bajada de la etapa 1'},
            {'es_name': 'zona_subida_2', 'csv_name': 'Zona_subidad_etapa_2',
             'definition': 'Zona 777 asociada a la subida de la etapa 2'},
            {'es_name': 'zona_bajada_2', 'csv_name': 'Zona_bajada_etapa_2',
             'definition': 'Zona 777 asociada a la bajada de la etapa 2'},
            {'es_name': 'zona_subida_3', 'csv_name': 'Zona_subidad_etapa_3',
             'definition': 'Zona 777 asociada a la subida de la etapa 3'},
            {'es_name': 'zona_bajada_3', 'csv_name': 'Zona_bajada_etapa_3',
             'definition': 'Zona 777 asociada a la bajada de la etapa 3'},
            {'es_name': 'zona_subida_4', 'csv_name': 'Zona_subidad_etapa_4',
             'definition': 'Zona 777 asociada a la subida de la etapa 4'},
            {'es_name': 'zona_bajada_4', 'csv_name': 'Zona_bajada_etapa_4',
             'definition': 'Zona 777 asociada a la bajada de la etapa 4'},
            {'es_name': 'mediahora_bajada_1', 'csv_name': 'mediahora_bajada_etapa_1',
             'definition': 'Media hora de la bajada asociada a la etapa 1'},
            {'es_name': 'mediahora_bajada_2', 'csv_name': 'mediahora_bajada_etapa_2',
             'definition': 'Media hora de la bajada asociada a la etapa 2'},
            {'es_name': 'mediahora_bajada_3', 'csv_name': 'mediahora_bajada_etapa_3',
             'definition': 'Media hora de la bajada asociada a la etapa 3'},
            {'es_name': 'mediahora_bajada_4', 'csv_name': 'mediahora_bajada_etapa_4',
             'definition': 'Media hora de la bajada asociada a la etapa 4'},
            {'es_name': 'parada_subida_1', 'csv_name': 'parada_subida_1',
             'definition': 'Código transantiago de la parada donde inició la etapa 1'},
            {'es_name': 'parada_subida_2', 'csv_name': 'parada_subida_2',
             'definition': 'Código transantiago de la parada donde inició la etapa 2'},
            {'es_name': 'parada_subida_3', 'csv_name': 'parada_subida_3',
             'definition': 'Código transantiago de la parada donde inició la etapa 3'},
            {'es_name': 'parada_subida_4', 'csv_name': 'parada_subida_4',
             'definition': 'Código transantiago de la parada donde inició la etapa 4'},
            {'es_name': 'parada_bajada_1', 'csv_name': 'parada_bajada_1',
             'definition': 'Código transantiago de la parada donde terminó la etapa 1'},
            {'es_name': 'parada_bajada_2', 'csv_name': 'parada_bajada_2',
             'definition': 'Código transantiago de la parada donde terminó la etapa 2'},
            {'es_name': 'parada_bajada_3', 'csv_name': 'parada_bajada_3',
             'definition': 'Código transantiago de la parada donde terminó la etapa 3'},
            {'es_name': 'parada_bajada_4', 'csv_name': 'parada_bajada_4',
             'definition': 'Código transantiago de la parada donde terminó la etapa 4'},
            {'es_name': 'periodo_bajada_1', 'csv_name': 'periodo_bajada_etapa_1',
             'definition': 'Período transantiago de bajada asociada a la etapa 1'},
            {'es_name': 'periodo_bajada_2', 'csv_name': 'periodo_bajada_etapa_2',
             'definition': 'Período transantiago de bajada asociada a la etapa 2'},
            {'es_name': 'periodo_bajada_3', 'csv_name': 'periodo_bajada_etapa_3',
             'definition': 'Período transantiago de bajada asociada a la etapa 3'},
            {'es_name': 'periodo_bajada_4', 'csv_name': 'periodo_bajada_etapa_4',
             'definition': 'Período transantiago de bajada asociada a la etapa 4'},
             {
                "es_name": "id_tarjeta",
                "csv_name": "id_tarjeta",
                "definition": "Identificador asociado a la tarjeta bip!.",
            },
            {
                "es_name": "id_viaje",
                "csv_name": "id_viaje",
                "definition": "Correlativo del viaje de la tarjeta bip!.",
            },
            {
                "es_name": "n_etapas_sin_bajada",
                "csv_name": "n_etapas_sin_bajada",
                "definition": "Número de etapas sin bajada del viaje.",
            },
            {
                "es_name": "ultima_etapa_con_bajada",
                "csv_name": "ultima_etapa_con_bajada",
                "definition": "Indicador de que la última etapa tiene bajada estimada. Toma el valor 1 en caso de que si sea.",
            },
            {
                "es_name": "contrato",
                "csv_name": "contrato",
                "definition": "Contrato de la transacción",
            },
            {
                "es_name": "mediahora_inicio_viaje_hora",
                "csv_name": "mediahora_inicio_viaje_hora",
                "definition": "Media hora en formato HH:mm:ss en el que se inició el viaje",
            },
            {
                "es_name": "mediahora_fin_viaje_hora",
                "csv_name": "mediahora_fin_viaje_hora",
                "definition": "Media hora en formato HH:mm:ss en el que finalizó el viaje",
            },
            {
                "es_name": "op_etapa_1",
                "csv_name": "operador_etapa_1",
                "definition": "Operador asociado a la primera etapa.",
            },
            {
                "es_name": "op_etapa_2",
                "csv_name": "operador_etapa_2",
                "definition": "Operador asociado a la segunda etapa.",
            },
            {
                "es_name": "op_etapa_3",
                "csv_name": "operador_etapa_3",
                "definition": "Operador asociado a la tercera etapa.",
            },
            {
                "es_name": "op_etapa_4",
                "csv_name": "operador_etapa_4",
                "definition": "Operador asociado a la cuarta etapa.",
            },
            {
                "es_name": "distancia_caminata_1",
                "csv_name": "distancia_caminata_1",
                "definition": "Distancia de transbordo (caminata) entre la etapa 1 y la etapa 2.",
            },
            {
                "es_name": "distancia_vehiculo_ruta_1",
                "csv_name": "distancia_vehiculo_ruta_1",
                "definition": "Distancia recorrida por vehículo en ruta durante la etapa 1.",
            },
            {
                "es_name": "distancia_euclidiana_vehiculo_ruta_1",
                "csv_name": "distancia_euclidiana_vehiculo_ruta_1",
                "definition": "Distancia euclidiana recorrida por vehículo en ruta durante la etapa 1.",
            },
            {
                "es_name": "distancia_caminata_2",
                "csv_name": "distancia_caminata_2",
                "definition": "Distancia de transbordo (caminata) entre la etapa 2 y la etapa 3.",
            },
            {
                "es_name": "distancia_vehiculo_ruta_2",
                "csv_name": "distancia_vehiculo_ruta_2",
                "definition": "Distancia recorrida por vehículo en ruta durante la etapa 2.",
            },
            {
                "es_name": "distancia_euclidiana_vehiculo_ruta_2",
                "csv_name": "distancia_euclidiana_vehiculo_ruta_2",
                "definition": "Distancia euclidiana recorrida por vehículo en ruta durante la etapa 2.",
            },
            {
                "es_name": "distancia_caminata_3",
                "csv_name": "distancia_caminata_3",
                "definition": "Distancia de transbordo (caminata) entre la etapa 3 y la etapa 4.",
            },
            {
                "es_name": "distancia_vehiculo_ruta_3",
                "csv_name": "distancia_vehiculo_ruta_3",
                "definition": "Distancia recorrida por vehículo en ruta durante la etapa 3.",
            },
            {
                "es_name": "distancia_euclidiana_vehiculo_ruta_3",
                "csv_name": "distancia_euclidiana_vehiculo_ruta_3",
                "definition": "Distancia euclidiana recorrida por vehículo en ruta durante la etapa 3.",
            },
            {
                "es_name": "distancia_vehiculo_ruta_4",
                "csv_name": "distancia_vehiculo_ruta_4",
                "definition": "Distancia recorrida por vehículo en ruta durante la etapa 4.",
            },
            {
                "es_name": "distancia_euclidiana_vehiculo_ruta_4",
                "csv_name": "distancia_euclidiana_vehiculo_ruta_4",
                "definition": "Distancia euclidiana recorrida por vehículo en ruta durante la etapa 4.",
            },
            {
                "es_name": "distancia_caminata_final",
                "csv_name": "distancia_caminata_final",
                "definition": "Suma de distancias de todos los transbordos (caminatas)",
            },
            {
                "es_name": "distancia_vehiculo_ruta_final",
                "csv_name": "distancia_vehiculo_ruta_final",
                "definition": "Suma de distancia total recorrida por vehiculos en ruta.",
            },
            {
                "es_name": "distancia_euclidiana_vehiculo_ruta_final",
                "csv_name": "distancia_euclidiana_vehiculo_rfinal",
                "definition": "Suma de distancia euclidiana total recorrida por vehículos en ruta.",
            },
            {
                "es_name": "tipo_corte_etapa_viaje",
                "csv_name": "tipo_corte_etapa_viaje",
                "definition": "Tipo de corte etapa/viaje.",
            },
            {
                "es_name": "proposito",
                "csv_name": "proposito",
                "definition": "Propósito para el cual se realiza el viaje",
            },
            {
                "es_name": "tiempo_entrada",
                "csv_name": "tiempo_entrada",
                "definition": "Tiempo de entrada a estaciones de Metro [min].",
            },
            {
                "es_name": "tiempo_espera_0",
                "csv_name": "tiempo_espera_0",
                "definition": "Tiempo de espera en la etapa 1 [min].",
            },
            {
                "es_name": "tiempo_viaje_vehiculo_1",
                "csv_name": "tiempo_viaje_vehiculo_1",
                "definition": "Tiempo de viaje en vehículo durante la etapa 1 [min].",
            },
            {
                "es_name": "tiempo_caminata_etapa_1",
                "csv_name": "tiempo_caminata_etapa_1",
                "definition": "Tiempo de caminata de la etapa 1 hacia la subida de la etapa 2 [min].",
            },
            {
                "es_name": "tiempo_espera_1",
                "csv_name": "tiempo_espera_1",
                "definition": "Tiempo de espera en la etapa 2 [min].",
            },
            {
                "es_name": "tiempo_viaje_vehiculo_2",
                "csv_name": "tiempo_viaje_vehiculo_2",
                "definition": "Tiempo de viaje en vehículo durante la etapa 2 [min].",
            },
            {
                "es_name": "tiempo_caminata_etapa_2",
                "csv_name": "tiempo_caminata_etapa_2",
                "definition": "Tiempo de caminata de la etapa 2 hacia la subida de la etapa 3 [min].",
            },
            {
                "es_name": "tiempo_espera_2",
                "csv_name": "tiempo_espera_2",
                "definition": "Tiempo de espera en la etapa 3 [min].",
            },
            {
                "es_name": "tiempo_viaje_vehiculo_3",
                "csv_name": "tiempo_viaje_vehiculo_3",
                "definition": "Tiempo de viaje en vehículo durante la etapa 3 [min].",
            },
            {
                "es_name": "tiempo_caminata_etapa_3",
                "csv_name": "tiempo_caminata_etapa_3",
                "definition": "Tiempo de caminata de la etapa 3 hacia la subida de la etapa 4 [min].",
            },
            {
                "es_name": "tiempo_espera_3",
                "csv_name": "tiempo_espera_3",
                "definition": "Tiempo de espera en la etapa 4 [min].",
            },
            {
                "es_name": "tiempo_viaje_vehiculo_4",
                "csv_name": "tiempo_viaje_vehiculo_4",
                "definition": "Tiempo de viaje en vehículo durante la etapa 4 [min].",
            },
            {
                "es_name": "tiempo_egreso",
                "csv_name": "tiempo_egreso",
                "definition": "Tiempo de egreso de estaciones de metro [min].",
            }
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Viajes.csv: Cada línea representa un viaje.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())

    def test__process_filters(self):
        date_range = {
            'range': {'tiempo_subida': {'gte': '2020-02-26||/d', 'lte': '2020-02-27||/d', 'format': 'yyyy-MM-dd',
                                        'time_zone': '+00:00'}}}
        int_range = {'range': {'n_etapas': {'gte': 5}}}

        expected_output = [{'field': 'Tiempo_subida', 'value': 'entre 2020-02-26 00:00:00 y 2020-02-27 23:59:59'},
                           {'field': 'Número_etapas', 'value': 5}]

        self.assertEqual(self.csv_helper._process_filters([date_range, int_range]), expected_output)


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestShapeCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.ShapeCSVHelper(None)

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Geometría_servicio.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago', 'definition': 'Código transantiago del servicio'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación',
             'definition': 'Fecha de inicio del programa de operación desde el que esta geometría es válida'},
            {'es_name': '', 'csv_name': 'Latitud', 'definition': 'Latitud'},
            {'es_name': '', 'csv_name': 'Longitud', 'definition': 'Longitud'},
            {'es_name': '', 'csv_name': 'Inicio_segmento_500m',
             'definition': 'Indica si el punto corresponde al inicio de un tramo de 500 metros (1: si, 0: no)'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Geometría_servicio.csv: Geometría del servicio.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestStopByRouteCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.StopByRouteCSVHelper(None)

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Secuencia_paradas.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'authRouteCode', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código transantiago del servicio'},
            {'es_name': 'userRouteCode', 'csv_name': 'Servicio_usuario', 'definition': 'Código usuario del servicio'},
            {'es_name': 'startDate', 'csv_name': 'Fecha_inicio_programa_operación',
             'definition': 'Fecha de inicio del programa de operación desde el que esta ruta es válida'},
            {'es_name': '', 'csv_name': 'Posición_en_ruta',
             'definition': 'Posición de la parada dentro de la secuencia de paradas del servicio'},
            {'es_name': '', 'csv_name': 'Latitud', 'definition': 'Latitud'},
            {'es_name': '', 'csv_name': 'Longitud', 'definition': 'longitud'},
            {'es_name': '', 'csv_name': 'Código_parada_transantiago', 'definition': 'Código transantiago de la parada'},
            {'es_name': '', 'csv_name': 'Código_parada_usuario', 'definition': 'Código usuario de la parada'},
            {'es_name': '', 'csv_name': 'Nombre_parada', 'definition': 'Nombre de la parada'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Secuencia_paradas.csv: paradas asignadas al servicio.\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestPaymentFactorCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.PaymentFactorCSVHelper(None, {})

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Distribución_de_validaciones.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'date', 'csv_name': 'Fecha', 'definition': 'Día en que se realizaron las validaciones'},
            {'es_name': 'dayType', 'csv_name': 'Tipo_día', 'definition': 'Tipo de día'},
            {'es_name': 'operator', 'csv_name': 'Id Operador',
             'definition': 'Identificador de empresa asociada a la zona paga'},
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa asociada a la zona paga'},
            {'es_name': 'assignation', 'csv_name': 'Asignación',
             'definition': 'Indica si el operador está asignado a la zona paga'},
            {'es_name': 'busStationId', 'csv_name': 'Identificador_zona_paga',
             'definition': 'Código que identifica la zona paga'},
            {'es_name': 'busStationName', 'csv_name': 'Nombre_zona_paga',
             'definition': 'Nombre de la parada donde se encuentra la zona paga'},
            {'es_name': 'total', 'csv_name': 'Total', 'definition': ''},
            {'es_name': 'sum', 'csv_name': 'Suman', 'definition': ''},
            {'es_name': 'subtraction', 'csv_name': 'Restan', 'definition': ''},
            {'es_name': 'neutral', 'csv_name': 'Neutras', 'definition': ''},
            {'es_name': 'factor', 'csv_name': 'Factor', 'definition': 'Factor de pago'},
            {'es_name': 'routes', 'csv_name': 'Servicios',
             'definition': 'Servicios que se detienen en esta parada, separados por el signo "-"'},
            {'es_name': 'transactions', 'csv_name': 'Validaciones',
             'definition': 'N° de validaciones por servicio, están separados por el signo "-" y su servicio asociado es el ubicado en la misma posición de la columna "Servicios"'},
            {'es_name': 'validatorId', 'csv_name': 'Id de validador',
             'definition': 'Identificador del validador asociado a la zona paga'},
            {'es_name': 'operatorTransactions', 'csv_name': 'Transacciones UN',
             'definition': 'Transacciones de la unidad de negocio. Un valor de -1 significa que no fue posible calcular este número.'},
            {'es_name': 'factorWithoutThreesomeMethodology', 'csv_name': 'Factor sin trío',
             'definition': 'Factor de pago sin la metodología de tríos Un valor de -1 significa que no fue posible calcular este número.'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Distribución_de_validaciones.csv: Cada línea representa las validaciones asociadas a un operador en una zona paga\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestBipCSVHelper(TestCase):

    def setUp(self):
        self.csv_helper = helper.BipCSVHelper(None, {})

    def test_get_data_file_name(self):
        self.assertEqual(self.csv_helper.get_data_file_name(), "Bip.csv")

    def test_get_column_dict(self):
        expected = [
            {'es_name': 'operator', 'csv_name': 'Operador', 'definition': 'Empresa que opera el servicio'},
            {'es_name': 'route', 'csv_name': 'Servicio_transantiago',
             'definition': 'Código de transantiago del servicio'},
            {'es_name': 'userRoute', 'csv_name': 'Servicio_usuario',
             'definition': 'Código de usuario del servicio (ejemplo: 506)'},
            {'es_name': 'validationTime', 'csv_name': 'Hora_validacion',
             'definition': 'Fecha y hora de la validación'},
            {'es_name': 'bipNumber', 'csv_name': 'Número Bip', 'definition': 'Número de la tarjeta bip'},
            {'es_name': 'source', 'csv_name': 'Fuente de dato',
             'definition': 'Bus, estación de metro, metrobus o totem validador.'}
        ]
        self.assertEqual(expected, self.csv_helper.get_column_dict())

    def test_get_file_description(self):
        expected = '\t\t- Bip.csv: archivo de transacciones bip, cada fila representa una validación bip\r\n'
        self.assertEqual(expected, self.csv_helper.get_file_description())
