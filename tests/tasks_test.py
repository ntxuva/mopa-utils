# -*- coding: utf-8 -*-

import unittest
from mopa import create_app


class TasksTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_should_fail_if_not_passing_api_key(self):
        rv = self.client.get('/tasks/send-monthly-report')
        self.assertEqual(403, rv.status_code)

    def test_should_fail_if_passing_wrong_api_key(self):
        headers = [('API_KEY', 'wrong')]
        rv = self.client.get('/tasks/send-monthly-report', headers=headers)
        self.assertEqual(403, rv.status_code)

    def test_should_pass_if_passing_right_api_key(self):
        headers = [('API_KEY', 'local')]
        rv = self.client.get('/tasks/send-monthly-report', headers=headers)
        self.assertEqual(200, rv.status_code)

    # @unittest.skip('Test is slow')
    def test_should_send_daily_report(self):
        headers = [('API_KEY', 'local')]
        rv = self.client.get('/tasks/send-daily-report', headers=headers)
        self.assertEqual(200, rv.status_code)

    # @unittest.skip('Test is slow')
    def test_should_send_weekly_report(self):
        headers = [('API_KEY', 'local')]
        rv = self.client.get('/tasks/send-weekly-report', headers=headers)
        self.assertEqual(200, rv.status_code)

    # @unittest.skip('Test is slow')
    def test_should_send_monthly_report(self):
        headers = [('API_KEY', 'local')]
        rv = self.client.get('/tasks/send-monthly-report', headers=headers)
        self.assertEqual(200, rv.status_code)
