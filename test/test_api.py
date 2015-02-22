"""
API test.
"""

import requests

from twisted.trial import unittest


class BaseTest(unittest.TestCase):
    baseUrl = "http://localhost:3000"

    def assertRequest(self, method, uri, data=None, expected_code=200, expected_body=''):
        url = self.baseUrl + uri
        resp = getattr(requests, method)(url, data=data)

        self.assertEqual(resp.status_code, expected_code)
        self.assertEqual(resp.text, expected_body)


class SubscriptionTest(BaseTest):
    def test_aliceBob(self):
        message = 'http://cuteoverload.files.wordpress.com/2014/10/unnamed23.jpg?w=750&h=1000'

        self.assertRequest('post', '/topic/alice')
        self.assertRequest('post', '/topic/bob')
        self.assertRequest('post', '/topic', data=message)
        self.assertRequest('get', '/topic/alice', expected_body=message)
        self.assertRequest('get', '/topic/alice', expected_code=204)
        self.assertRequest('delete', '/topic/bob')
        self.assertRequest('get', '/topic/bob', expected_code=404)

    def test_multipleTopics(self):
        message1 = 'msg1'
        message2 = 'msg2'

        self.assertRequest('post', '/topic1/alice')
        self.assertRequest('post', '/topic2/bob')
        self.assertRequest('post', '/topic2/alice')
        self.assertRequest('post', '/topic1', data=message1)
        self.assertRequest('post', '/topic2', data=message1)
        self.assertRequest('post', '/topic1/charlie')
        self.assertRequest('delete', '/topic2/alice')
        self.assertRequest('post', '/topic1', data=message2)
        self.assertRequest('post', '/topic2', data=message2)
        self.assertRequest('post', '/topic1/alice')

        self.assertRequest('get', '/topic1/alice', expected_body=message1)
        self.assertRequest('get', '/topic1/alice', expected_body=message2)
        self.assertRequest('get', '/topic1/alice', expected_code=204)
        self.assertRequest('get', '/topic2/alice', expected_code=404)

        self.assertRequest('get', '/topic1/bob', expected_code=404)
        self.assertRequest('get', '/topic2/bob', expected_body=message1)
        self.assertRequest('get', '/topic2/bob', expected_body=message2)
        self.assertRequest('get', '/topic2/bob', expected_code=204)
        self.assertRequest('delete', '/topic1/bob', expected_code=404)
        self.assertRequest('delete', '/topic2/bob')
        self.assertRequest('delete', '/topic2/bob', expected_code=404)

        self.assertRequest('get', '/topic1/charlie', expected_body=message2)
        self.assertRequest('get', '/topic1/charlie', expected_code=204)
        self.assertRequest('get', '/topic2/charlie', expected_code=404)
        self.assertRequest('delete', '/topic1/charlie')
