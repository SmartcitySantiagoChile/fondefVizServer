#!/usr/bin/env python
import csv
import utm
import json

# This script generates a geojson file from the ADAPTRAP's
# Diccionario-Zonificaciones.csv file.
#
# Just change the input and output paths below
#
# How to run:
# 1. Place the 'Diccionario-Zonificaciones.csv' file on this folder.
# 2. Run: $ python gen_777geojson_from_adatrap_dict.py
# 3. Collect the generated '777.geojson' file.
#

# ----------------------------------------------------------------
# configuration
dict_filename = "Diccionario-Zonificaciones.csv"
geojson_filename = "777.geojson"
csv_delimiter = ';'
csv_number_of_columns = 5  # only consider rows with this number of fields
zone_id_column = 0
utm_x_column = 1
utm_y_column = 2
zonification_column = 4
zonification_key = "diseno_777"
# ----------------------------------------------------------------


# READ
# ----------------------------------------------------------------
print(" - reading zonification from file: %s" % dict_filename)
zonification = dict()
with open(dict_filename, 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=csv_delimiter)
    for row in reader:

        # filter
        if len(row) != csv_number_of_columns:
            continue

        # valid zonification
        if row[zonification_column] == zonification_key:
            zone_id = row[zone_id_column]
            utm_x = row[utm_x_column]
            utm_y = row[utm_y_column]
            try:
                latlon = utm.to_latlon(float(utm_x), float(utm_y), 19, 'H')
            except Exception as e:
                continue

            # new zonification
            if zone_id not in zonification:
                zonification[zone_id] = list()

            # reduce final size by forcing 4 decimals (11[m] precision)
            # https://gis.stackexchange.com/questions/8650/measuring-accuracy-of-latitude-and-longitude
            lon = round(latlon[0], 4)
            lat = round(latlon[1], 4)

            # append
            zonification[zone_id].append([lat, lon])
print(" - found %d zones" % len(zonification))


# FORMAT
# ----------------------------------------------------------------
# create geojson dictionary
print(" - formatting as zonification as a geojson dictionary")
geojson = dict()
geojson['type'] = "FeatureCollection"
geojson['features'] = list()
for zone_id in zonification:
    polygon = zonification[zone_id]
    if len(polygon) < 3:
        continue
    coordinates = list()
    coordinates.append(polygon)

    properties = dict()
    properties['id'] = int(float(zone_id))

    geometry = dict()
    geometry['type'] = "Polygon"
    geometry['coordinates'] = coordinates

    feature = dict()
    feature['type'] = "Feature"
    feature['properties'] = properties
    feature['geometry'] = geometry

    geojson['features'].append(feature)


# WRITE
# ----------------------------------------------------------------
# write to file
print(" - writing geojson to file: %s" % geojson_filename)
with open(geojson_filename, 'w') as fp:
    json.dump(geojson, fp)

print(" - done :)")
