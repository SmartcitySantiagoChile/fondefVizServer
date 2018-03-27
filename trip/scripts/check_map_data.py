#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MODO DE USO:

Modificar variable 'input_filename', para que apunte al archivo CSV que se
entrega a elastic search, mediante logstash.

Luego ejecutar:
    $ ./check_map_data.py > check_results.txt

    Esto creará un archivo check_results.txt, con los datos que DEBE RETORNAR
    la consulta realizada a elastic search por el server, al crear el mapa.

    Es posible correr esto sobre una versión más pequeña del archivo,
    utilizando algo como:
    1. $ head -n 10000 2016-03-14.viajes_visualizacion > chunk.csv
    2. modificar 'input_filename' a 'chunk.csv'
    3. $ ./check_map_data.py > check_results.txt

OBS: Esto fue probado dejando este script directamente en la carpeta de
logstash y luego ejecutandolo.
"""

import csv

sectors = dict()
sectors['Lo Barnechea'] = [202, 642]
sectors['Centro'] = [267, 276, 285, 286]
sectors['Providencia'] = [175, 176, 179]
sectors['Las Condes'] = [207, 215, 216]
sectors['Vitacura'] = [191, 192, 193, 195, 196]
sectors['Quilicura'] = [557, 831]

sector_name = 'Centro'
input_filename = 'chunk.csv'
input_filename = '2016-03-14.viajes_visualizacion'

csv_delimiter = '|'
csv_number_of_columns = 27  # only consider rows with this number of fields
stat_keys = ['n_etapas', 'tviaje', 'distancia_ruta', 'distancia_eucl']
stat_multipliers = [1, 1, 1/1000.0, 1/1000.0]

results = dict()

print(" => Stat Names: %s" % stat_keys)
print(" => Checking sector '%s': %s" % (sector_name, sectors[sector_name]))
print(" => Opening file: %s" % input_filename)
with open(input_filename, 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=csv_delimiter)
    for row in reader:

        # filter invalid rows
        if len(row) != csv_number_of_columns:
            continue

        # valid zona_bajada
        zona_bajada = int(float(row['zona_bajada']))
        if zona_bajada in sectors[sector_name]:

            # select by zona_subida
            zona_subida = int(float(row['zona_subida']))

            # new data
            if zona_subida not in results:
                item = dict()
                item['count'] = 0
                item['stat_sums'] = [0] * len(stat_keys)
                results[zona_subida] = item

            # compute stats
            zone = results[zona_subida]
            zone['count'] += 1
            for idx, key in enumerate(stat_keys):
                zone['stat_sums'][idx] += float(row[key])
            results[zona_subida] = zone


print(" => Writing results to screen")
print("zona_subida, count, %s" % stat_keys)
for zone_id in results:
    zone = results[zone_id]
    count_ = zone['count']
    sums_ = zone['stat_sums']

    values_ = [0] * len(stat_keys)
    str_ = " %3d, %5d" % (zone_id, count_)
    if count_ > 0:
        for idx, key in enumerate(stat_keys):
            val_ = sums_[idx] * stat_multipliers[idx] / count_
            values_[idx] = val_
            str_ += ", %10.2f" % val_
    else:
        str_ += (", %10.2f" % 0) * len(stat_keys)

    print(str_)
