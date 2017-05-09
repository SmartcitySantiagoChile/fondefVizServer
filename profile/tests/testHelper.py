from django.test import Client
# python stuf
import json

# Create your tests here.
class TestHelper():
    """ test helper """

    def __init__(self, testInstance):
        self.testInstance = testInstance

    def makeGetRequest(self, url, params = {}):

        c = Client()
        response = c.get(url, params)
        self.testInstance.assertEqual(response.status_code, 200)

        return response

    def makePostRequest(self, url, params = {}):

        c = Client()
        response = c.post(url, params)
        self.testInstance.assertEqual(response.status_code, 200)

        return response

    def printJson(self, jsonResponse):

        print json.dumps(jsonResponse,
                sort_keys=True,
                indent=4,
                separators=(',', ': '))
