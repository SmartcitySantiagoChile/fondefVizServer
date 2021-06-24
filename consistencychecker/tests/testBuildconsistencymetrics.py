from io import StringIO
from unittest.mock import MagicMock

from unittest import mock
from django.core.management import call_command
from django.test import TestCase


class BuildconsistencymetricsTest(TestCase):

    @mock.patch('consistencychecker.models.Consistency.objects.create')
    @mock.patch('datamanager.helper.FileManager.get_file_list')
    @mock.patch('datamanager.helper.FileManager.get_time_period_list_by_file_from_elasticsearch')
    def test_command_output(self, get_time_period_list, get_file_list, create):
        get_time_period_list.return_value = {'2020-04-20':{'profile': [1,2,3,4], "odbyroute": [1,2,3,4], "trip": [1,2,3,4]}}

        get_file_list.return_value = {"key": [{
            "name": "2020-04-20.profile",
            "lines": 1,
            "docNumber": 1,
            'path': "/home/bastianleaf/Documents/Trabajo/datos",
        }]}
        create = MagicMock()
        create.date = "2020-02-20"
        out = StringIO()
        call_command('buildconsistencymetrics', stdout=out)
        self.assertIn("Warning: 2020-04-20.profile has wrong time period ids", out.getvalue())
        self.assertIn('All metrics recalculated.', out.getvalue())
