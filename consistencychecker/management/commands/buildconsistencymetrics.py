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
        date_dict = defaultdict(lambda: {key: {'lines': 0, 'docNumber': 0} for key in keys_list})
        filemanager = FileManager()
        file_dict = filemanager.get_file_list()
        for key in file_dict.keys():
            for file in file_dict[key]:
                date = file['name'].split(".")[0]
                date_info = {key: {'lines': file['lines'], 'docNumber': file['docNumber']}}
                date_dict[date].update(date_info)

        for date in date_dict.keys():
            params = dict(date=datetime.strptime(date, '%Y-%m-%d'))
            for index_name in keys_list:
                aux = dict()
                aux['{0}_file'.format(index_name)] = date_dict[date][index_name]['lines']
                aux['{0}_index'.format(index_name)] = date_dict[date][index_name]['docNumber']
                params.update(aux)

            Consistency.objects.create(**params)
