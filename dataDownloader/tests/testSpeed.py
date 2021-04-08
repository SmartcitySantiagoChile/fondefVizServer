from unittest import mock

from django.test import TestCase, override_settings

from dataDownloader.csvhelper import speed


@override_settings(ES_CLIENT=mock.MagicMock(return_value=None))
class TestSpeedDataWithFormattedShape(TestCase):

    def test_build_file(self):
        self.assertEqual(1, 1)
        speed_obj = speed.SpeedDataWithFormattedShape(es_query)


