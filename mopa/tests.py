import os
import flask
import unittest
import tempfile

class SMSViewTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])


class ExporterTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TasksTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
