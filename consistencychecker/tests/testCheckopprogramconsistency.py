from io import StringIO
from unittest.mock import MagicMock
from consistencychecker.management.commands import checkopprogramconsistency
import mock
from django.core.management import call_command
from django.test import TestCase



class CheckopprogramconsistencyTest(TestCase):

    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESOPDataHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESShapeHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESStopHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESStopByRouteHelper')
    def test_command_output(self, stopbyroute_helper, stop_helper, shape_helper, opdata_helper):
        stopbyroute_helper.return_value = mock.MagicMock()
        stop_helper.return_value = mock.MagicMock()
        shape_helper.return_value = mock.MagicMock()
        opdata_helper.return_value = mock.MagicMock()
        shape_helper.get_available_days.return_value = ['2020-05-03']
        out = StringIO()
        call_command('checkopprogramconsistency', stdout=out)
        #self.assertIn('All metrics recalculated.', out.getvalue())
