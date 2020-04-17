from django.core.management.base import BaseCommand

from consistencychecker.models import Consistency


class Command(BaseCommand):
    help = 'It cleans and recalculates Consistency metrics'

    def handle(self, *args, **options):
        Consistency.objects.all().delete()
