# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from esapi.helper.busstationdistribution import ESBusStationDistributionHelper
from esapi.helper.odbyroute import ESODByRouteHelper
from esapi.helper.profile import ESProfileHelper
from esapi.helper.resume import ESResumeStatisticHelper
from esapi.helper.shape import ESShapeHelper
from esapi.helper.speed import ESSpeedHelper
from esapi.helper.stop import ESStopHelper
from esapi.helper.stopbyroute import ESStopByRouteHelper
from esapi.helper.trip import ESTripHelper


class Command(BaseCommand):
    help = 'Delete indexes in elasticsearch'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        helpers = [
            ESStopHelper(),
            ESStopByRouteHelper(),
            ESProfileHelper(),
            ESSpeedHelper(),
            ESTripHelper(),
            ESShapeHelper(),
            ESODByRouteHelper(),
            ESResumeStatisticHelper(),
            ESBusStationDistributionHelper()
        ]

        for helper in helpers:
            settings.ES_CLIENT.indices.delete(index=helper.index_name, ignore=[400, 404])
            self.stdout.write(self.style.SUCCESS('Index {0} deleted successfully'.format(helper.index_name)))
