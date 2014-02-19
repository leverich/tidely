#!/usr/bin/env python

from webtest import TestApp
import unittest
import web

import main

class TestTidelyWSGI(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(main.application)

    def test_tidely_index(self):
        response = self.app.get('/')
        self.assertEquals(response.status_int, 200)
        self.assertTrue('box' in response)

    def test_tidely_detail(self):
        response = self.app.get('/detail?current_site=San+Francisco+Bay+Entrance')
        self.assertEquals(response.status_int, 200)
        self.assertTrue('tidetable' in response)

    def test_tidely_graph(self):
        response = self.app.get('/graph?site=San+Francisco+Bay+Entrance')
        self.assertEquals(response.status_int, 200)
        self.assertTrue(response.content_length > 0)
        self.assertEquals(response.content_type, 'image/png')

if __name__ == '__main__':
    unittest.main()
