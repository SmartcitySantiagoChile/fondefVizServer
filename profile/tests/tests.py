from django.test import TestCase

# python stuf
import json

from testHelper import TestHelper
# Create your tests here.

class TimePerStreetTestCase(TestCase):
    """ test for views """
    URL_PREFIX = '/profile/'

    def setUp(self):
        """ case configuration """
        self.testHelper = TestHelper(self)

    def testGetExpeditionData(self):

        url = 'getExpeditionData'
        url = self.URL_PREFIX + url
        response = self.testHelper.makeGetRequest(url, {})

        jsonResponse = json.loads(response.content)
        
        self.assertEqual(jsonResponse['status']['code'], 400)
        self.assertEqual(jsonResponse['trips'], {})

    def testExpeditionView(self):

        url = 'expedition'
        url = self.URL_PREFIX + url
        response = self.testHelper.makeGetRequest(url)


