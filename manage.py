# -*- coding: utf-8 -*-

import os
import subprocess
import sys

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'vendor'))

from mopa import create_app
from flask import Flask, g, jsonify, url_for
from flask_script import Manager, Shell

app = create_app()
manager = Manager(app)


def make_shell_context():
    return dict(app=app)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """Runs unit tests and presents coverage report"""
    tests = subprocess.call(['python', '-c', "import os; import sys; sys.path.insert(1, os.path.join(os.path.abspath('.'), 'vendor')); import tests as tests; tests.run()"])
    sys.exit(tests)


@manager.command
def list_routes():
    """Lists all public and static routes"""
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print line


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run()

@manager.command
def runserver_secure():
    app.run('0.0.0.0', ssl_context='adhoc')

if __name__ == '__main__':
    manager.run()
