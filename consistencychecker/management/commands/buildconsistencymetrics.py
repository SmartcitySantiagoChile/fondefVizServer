import os
from collections import defaultdict
from datetime import datetime

from django.core.management.base import BaseCommand

from consistencychecker.models import Consistency
from datamanager.helper import FileManager
from localinfo.helper import get_periods_dict, get_valid_time_period_date, check_period_list_id


class Command(BaseCommand):
    help = 'It cleans and recalculates Consistency metrics'

    def handle(self, *args, **options):
        Consistency.objects.all().delete()
        keys_list = ["profile", "speed", "bip", "odbyroute", "trip", "paymentfactor", "general"]
        date_dict = defaultdict(lambda: {key: {'lines': 0, 'docNumber': 0} for key in keys_list})
        filemanager = FileManager()
        file_dict = filemanager.get_file_list()

        # get dict with file: time period values
        timeperiod_files_dict = filemanager.get_time_period_list_by_file_from_elasticsearch()
        # get dict with id : time period values
        valid_period_dict = get_periods_dict()
        for key in valid_period_dict.keys():
            valid_period_dict[key] = [period_dict["value"] for period_dict in valid_period_dict[key]]

        # check file_dict
        for key in file_dict.keys():
            for file in file_dict[key]:
                # get file info
                date = file['name'].split(".")[0]
                index = file['name'].split(".")[1]

                # check if valid period id
                valid_time_period_id = get_valid_time_period_date([date])[1]
                es_time_period_list = timeperiod_files_dict[date][index]
                correct_time_period_list = valid_period_dict[valid_time_period_id]
                correct_time_period_ids = check_period_list_id(es_time_period_list)

                if not es_time_period_list:
                    self.stdout.write(f"Warning: {date}.{index} is not in Elasticsearch")
                else:
                    result = set(es_time_period_list).issubset(correct_time_period_list)
                    if not result:
                        self.stdout.write(f"Warning: {date}.{index} has wrong time period ids ")
                        self.stdout.write(f"Warning: the correct time period ids for {date}.{index} are {correct_time_period_ids} ")
                date_info = {key: {'lines': file['lines'], 'docNumber': file['docNumber'],
        }}
                date_dict[date].update(date_info)
        for date in date_dict.keys():
            params = dict(date=datetime.strptime(date, '%Y-%m-%d'))
            authority_period_version = set()
            authority_period_index_version = set()
            for index_name in keys_list:
                aux = dict()
                aux['{0}_file'.format(index_name)] = date_dict[date][index_name]['lines']
                aux['{0}_index'.format(index_name)] = date_dict[date][index_name]['docNumber']
                if index_name in ["profile", "trip", "odbyroute"]:
                    valid_time_period_id = get_valid_time_period_date([date])[1]
                    authority_period_version.add(valid_time_period_id)
                    es_time_period_list = timeperiod_files_dict[date][index_name]
                    correct_time_period_ids = check_period_list_id(es_time_period_list)
                    authority_period_index_version = authority_period_index_version.union(set(correct_time_period_ids))
                params.update(aux)
            aux = dict()
            aux["authority_period_version"] = authority_period_version.pop()
            aux["authority_period_index_version"] = list(authority_period_index_version)
            params.update(aux)
            create = Consistency.objects.create(**params)
            self.stdout.write(str(create.date) + " created.")
        self.stdout.write("All metrics recalculated.")
