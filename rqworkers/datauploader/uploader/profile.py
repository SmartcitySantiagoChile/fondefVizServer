# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .datafile import DataFile, get_timestamp

import csv
import io


class ProfileFile(DataFile):
    """ Class that represents a profile file. """

    def __init__(self, datafile):
        DataFile.__init__(self, datafile)

    def makeDocs(self):
        with io.open(self.datafile, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                path = self.getPath()
                timestamp = get_timestamp()
                operator = row['operator']
                route = row['route']
                user_route = row['userRoute']
                shape_route = row['shapeRoute']
                license_plate = row['licensePlate']
                auth_stop_code = row['authStopCode']
                user_stop_name = row['userStopName']
                expedition_start_time = row['expeditionStartTime']
                expedition_end_time = row['expeditionEndTime']
                fulfillment = row['fulfillment']
                expedition_stop_order = row['expeditionStopOrder']
                expedition_day_id = row['expeditionDayId']
                stop_distance_from_path_start = row['stopDistanceFromPathStart']
                expanded_boarding = row['expandedBoarding']
                expanded_alighting = row['expandedAlighting']
                load_profile = row['loadProfile']
                bus_capacity = row['busCapacity']
                expedition_stop_time = row['expeditionStopTime']
                user_stop_code = row['userStopCode']
                time_period_in_start_time = row['timePeriodInStartTime']
                time_period_in_stop_time = row['timePeriodInStopTime']
                if expedition_stop_time == '-':
                    expedition_stop_time = "0"
                    time_period_in_stop_time = ""
                day_type = row['dayType']
                bus_station = row['busStation']
                transactions = row['transactions']
                half_hour_in_start_time = row['halfHourInStartTime']
                half_hour_in_stop_time = row['halfHourInStopTime']
                yield {
                    "_source": {
                        "path": path,
                        "timestamp": timestamp,
                        "operator": operator,
                        "route": route,
                        "userRoute": user_route,
                        "shapeRoute": shape_route,
                        "licensePlate": license_plate,
                        "authStopCode": auth_stop_code,
                        "userStopName": user_stop_name,
                        "expeditionStartTime": expedition_start_time,
                        "expeditionEndTime": expedition_end_time,
                        "fulfillment": fulfillment,
                        "expeditionStopOrder": expedition_stop_order,
                        "expeditionDayId": expedition_day_id,
                        "stopDistanceFromPathStart": stop_distance_from_path_start,
                        "expandedBoarding": expanded_boarding,
                        "expandedAlighting": expanded_alighting,
                        "loadProfile": load_profile,
                        "busCapacity": bus_capacity,
                        "expeditionStopTime": expedition_stop_time,
                        "userStopCode": user_stop_code,
                        "timePeriodInStartTime": time_period_in_start_time,
                        "timePeriodInStopTime": time_period_in_stop_time,
                        "dayType": day_type,
                        "busStation": bus_station,
                        "transactions": transactions,
                        "halfHourInStartTime": half_hour_in_start_time,
                        "halfHourInStopTime": half_hour_in_stop_time
                    }
                }

    def getHeader(self):
        return 'operator|route|userRoute|shapeRoute|licensePlate|authStopCode|userStopName|expeditionStartTime|expeditionEndTime|fulfillment|expeditionStopOrder|expeditionDayId|stopDistanceFromPathStart|#Subidas|#SubidasLejanas|Subidastotal|expandedBoarding|#Bajadas|#BajadasLejanas|Bajadastotal|expandedAlighting|loadProfile|busCapacity|TiempoGPSInterpolado|TiempoPrimeraTrx|TiempoGPSMasCercano|expeditionStopTime|nSubidasTmp|userStopCode|timePeriodInStartTime|timePeriodInStopTime|dayType|busStation|transactions|halfHourInStartTime|halfHourInStopTime'
