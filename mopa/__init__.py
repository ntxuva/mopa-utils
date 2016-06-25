# -*- coding: utf-8 -*-
"""
    mopa
    ----

    Mopa external utitities
"""
import os
import sys

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

__version__ = '0.1.1'


# Define the WSGI application object and configure
app = Flask(__name__)
app.config.from_object('config')

# Define the database object which are imported
# by modules and controllers
db = SQLAlchemy(app)


def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file
    in the instance directory.

    If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.
    """
    filename = os.path.join(app.instance_path, filename)

    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print('Error: No secret key. Create it with:')
        full_path = os.path.dirname(filename)
        if not os.path.isdir(full_path):
            print('mkdir -p {filename}'.format(filename=full_path))
        print('head -c 24 /dev/urandom > {filename}'.format(filename=filename))
        sys.exit(1)

if not app.config['DEBUG']:
    # install_secret_key(app)
    pass


@app.errorhandler(404)
def not_found(error):
    # Setup HTTP error handling
    return render_template('404.html'), 404
