from io import StringIO

import mock
from django.core.management import call_command
from django.test import TestCase


class CheckopprogramconsistencyTest(TestCase):

    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESOPDataHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESShapeHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESStopHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESStopByRouteHelper')
    def test_command_output_missing_date(self, stopbyroute_helper, stop_helper, shape_helper, opdata_helper):
        stopbyroute_helper.return_value = mock.MagicMock()
        shape_helper.return_value.get_available_days.return_value = ['2020-06-03']
        opdata_helper.return_value.get_available_days.return_value = ['2020-05-03']
        stop_helper.return_value.get_available_days.return_value = ['2020-05-03']

        out = StringIO()
        call_command('checkopprogramconsistency', stdout=out)
        expected_out = "Missing 2020-05-03 date in Shape\nMissing 2020-06-03 date in Stop\n" \
                       "Missing 2020-06-03 date in OPData\n"
        self.assertIn(expected_out, out.getvalue())

    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.helper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESOPDataHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESShapeHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESStopHelper')
    @mock.patch('consistencychecker.management.commands.checkopprogramconsistency.ESStopByRouteHelper')
    def test_command_output_missing_date(self, stopbyroute_helper, stop_helper, shape_helper, opdata_helper, helper):
        shape_helper.return_value.get_available_days.return_value = ['2020-05-03']
        opdata_helper.return_value.get_available_days.return_value = ['2020-05-03']
        stop_helper.return_value.get_available_days.return_value = ['2020-05-03']
        get_data_from_date = mock.MagicMock(hits=[{'authRouteCode': 'B01'}])
        shape_helper.return_value.get_data_from_date.return_value.execute.return_value = get_data_from_date
        stopbyroute_helper.return_value.get_stop_list.return_value = True
        out = StringIO()
        call_command('checkopprogramconsistency', stdout=out)
        # expected_out = "Missing 2020-05-03 date in Shape\nMissing 2020-06-03 date in Stop\n" \
        #               "Missing 2020-06-03 date in OPData\n"
        # self.assertIn(expected_out, out.getvalue())
        print(out.getvalue())
