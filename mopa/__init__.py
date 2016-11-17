# -*- coding: utf-8 -*-

import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_reggie import Reggie
from flask_cors import CORS

from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.cache import SimpleCache

import yaml
import logging
from logging.config import dictConfig

# dependencies / extensions
db = SQLAlchemy()
reggie = Reggie()
cors = CORS()
cache = SimpleCache()

from .infrastructure import (CustomJSONEncoder)


def create_app(config_name=None, main=True):
    """Create an application instance."""
    cfg = os.path.join(os.getcwd(), 'config.py') if os.path.exists('config.py') else os.path.join(os.getcwd(), 'mopa/config.py')

    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config['JSON_PRETTYPRINT_REGULAR'] = False
    app.config.from_pyfile(cfg)

    try:
        logging.config.dictConfig(yaml.load(file(os.path.join(app.config['BASE_DIR'], '../logging.yaml'),'r')))
    except Exception, e:
        pass
        # print "Error configurating logger ", str(e)

    # initialize extensions
    db.init_app(app)
    reggie.init_app(app)
    # logging.getLogger('flask_cors').level = logging.CRITICAL
    # cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # One line of code to cut our Flask page load times by 60%
    # https://blog.socratic.org/the-one-weird-trick-that-cut-our-flask-page-load-time-by-70-87145335f679#.8r14wvy5w
    app.jinja_env.cache = {}

    # register blueprints
    from .views import bp as api_blueprint
    app.register_blueprint(api_blueprint)

    from .tasks import bp as tasks_blueprint
    app.register_blueprint(tasks_blueprint, url_prefix='/tasks')

    return app
