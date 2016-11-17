import os
import sys
import subprocess
import unittest
import coverage


def run():
    os.environ['FLASK_CONFIG'] = 'testing'

    # start coverage engine
    cov = coverage.Coverage(branch=True)
    cov.start()

    # run tests
    suite = unittest.TestLoader().discover('.', pattern='*test.py')
    ok = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()

    # print coverage report
    cov.stop()
    # cov.save()
    print('\n\nCoverage Summary:')
    cov.report(omit=['manage.py', 'tests/*', 'venv*/*', 'lib/*', 'vendor/*'])
    # basedir = os.path.abspath(os.path.dirname(__file__))
    # covdir = os.path.join(basedir, 'tmp/coverage')
    # cov.html_report(directory=covdir)
    # print('HTML version: file://%s/index.html' % covdir)
    cov.erase()
    sys.exit(0 if ok else 1)
