from django.utils import timezone

from django.test import TestCase

from localinfo.helper import get_op_route, get_op_routes_dict
from localinfo.models import OPDictionary


class TestHelperUtils(TestCase):
    def test_get_custom_routes_dict(self):
        dict = {'T101 00I': '101 Ida', 'T101 00R': '101 Regreso', 'T112 00I': '112 Ida'}
        time_at = timezone.now()
        for key in dict:
            OPDictionary.objects.create(auth_route_code=key, route_type=dict[key],
                                        op_route_code=key, user_route_code=key, created_at=time_at,
                                        updated_at=time_at)
        query = get_op_routes_dict()
        self.assertDictEqual(dict, query)

    def test_get_op_route(self):
        auth_code = 'T101 00I'
        op_code = '101I'
        OPDictionary.objects.create(auth_route_code=auth_code, op_route_code=op_code)
        query = get_op_route(auth_code)
        self.assertEqual(op_code, query)

    def test_get_op_route_wrong_code(self):
        self.assertIsNone(get_op_route('T0000'))
