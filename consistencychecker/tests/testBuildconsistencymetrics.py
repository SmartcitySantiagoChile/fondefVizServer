from io import StringIO
from unittest.mock import MagicMock

from unittest import mock
from django.core.management import call_command
from django.test import TestCase


class BuildconsistencymetricsTest(TestCase):

    @mock.patch('consistencychecker.models.Consistency.objects.create')
    @mock.patch('datamanager.helper.FileManager.get_file_list')
    def test_command_output(self, get_file_list, create):
        get_file_list.return_value = {"key": [{
            "name": "2020-04-20",
            "lines": 1,
            "docNumber": 1
        }]}
        create = MagicMock()
        create.date = "2020-02-20"
        out = StringIO()
        call_command('buildconsistencymetrics', stdout=out)
        self.assertIn('All metrics recalculated.', out.getvalue())
