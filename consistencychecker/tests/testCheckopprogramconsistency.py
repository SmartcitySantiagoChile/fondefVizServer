from io import StringIO
from unittest.mock import MagicMock

import mock
from django.core.management import call_command
from django.test import TestCase


class CheckopprogramconsistencyTest(TestCase):

    @mock.patch('checkopprogramconsistency.ESOPDataHelper')
    @mock.patch('checkopprogramconsistency.ESShapeHelper')
    @mock.patch('checkopprogramconsistency.ESStopHelper')
    @mock.patch('checkopprogramconsistency.ESStopByRouteHelper')
    def test_command_output(self, stopbyroute_helper, stop_helper, shape_helper, opdata_helper):

        out = StringIO()
        call_command('checkopprogramconsistency', stdout=out)
        self.assertIn('All metrics recalculated.', out.getvalue())
