# -*- coding: utf-8 -*-

import os
import unittest
import tempfile

import flask
from mopa import create_app, db

class APITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(200, rv.status_code)

    def test_404(self):
        rv = self.client.get('/404')
        self.assertEqual(404, rv.status_code)
