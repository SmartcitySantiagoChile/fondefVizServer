from collections import defaultdict
from datetime import datetime

from django.core.management.base import BaseCommand

from consistencychecker.models import Consistency
from datamanager.helper import FileManager


class Command(BaseCommand):
    help = 'It cleans and recalculates Consistency metrics'

    def handle(self, *args, **options):
        Consistency.objects.all().delete()
        keys_list = ["profile", "speed", "bip", "odbyroute", "trip", "paymentfactor", "general"]
        date_dict = defaultdict()
        filemanager = FileManager()
        file_dict = filemanager.get_file_list()

        for key in file_dict.keys():
            for file in file_dict[key]:
                date = file['name'].split(".")[0]
                date_info = {key: {'lines': file['lines'], 'docNumber': file['docNumber']}}
                if date in date_dict:
                    date_dict[date].update(date_info)
                else:
                    date_dict[date] = date_info

        for date in date_dict.keys():
            for key in keys_list:
                if not key in date_dict[date]:
                    date_dict[date].update({key: {"lines": 0, "docNumber": 0}})
            date_split = date.split("-")
            print(date)
            print(int(date_split[2]))
            Consistency.objects.create(date=datetime(int(date_split[0]), int(date_split[1]), int(date_split[2])),
                                       profile_file=date_dict[date]['profile']['lines'],
                                       profile_index=date_dict[date]['profile']['docNumber'],
                                       speed_file=date_dict[date]['speed']['lines'],
                                       speed_index=date_dict[date]['speed']['docNumber'],
                                       bip_file=date_dict[date]['bip']['lines'],
                                       bip_index=date_dict[date]['bip']['docNumber'],
                                       odbyroute_file=date_dict[date]['odbyroute']['lines'],
                                       odbyroute_index=date_dict[date]['odbyroute']['docNumber'],
                                       trip_file=date_dict[date]['trip']['lines'],
                                       trip_index=date_dict[date]['trip']['docNumber'],
                                       paymentfactor_file=date_dict[date]['paymentfactor']['lines'],
                                       paymentfactor_index=date_dict[date]['paymentfactor']['docNumber'],
                                       general_index=date_dict[date]['general']['lines'],
                                       general_file=date_dict[date]['general']['docNumber'])
