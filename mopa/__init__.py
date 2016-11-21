# -*- coding: utf-8 -*-

import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_reggie import Reggie
from flask_cors import CORS

import logging, logging.config, yaml
from logging.handlers import RotatingFileHandler, SMTPHandler

# dependencies / extensions
db = SQLAlchemy()
reggie = Reggie()
cors = CORS()

from .infrastructure import (CustomJSONEncoder)


def setup_logging(app):
    config = app.config

    date_format = '%Y-%m-%d %H:%M:%S'
    simple_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    complex_format = """
        Message type:       %(levelname)s
        Location:           %(pathname)s:%(lineno)d
        Module:             %(module)s
        Function:           %(funcName)s
        Time:               %(asctime)s

        Message:

        %(message)s
    """
    simple_formatter = logging.Formatter(simple_format, date_format)
    complex_formatter = logging.Formatter(complex_format, date_format)

    log_file_path = os.path.join(app.config['APP_ROOT'],'data/logs/mopa.log')

    file_handler = RotatingFileHandler(log_file_path, maxBytes=10485760, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(simple_formatter)

    mail_handler = SMTPHandler(
        (config['SMTP_HOST'], config['SMTP_PORT']),
        config['SMTP_USERNAME'],
        config['ADMINS'],
        '[Mopa] Bug log',
        credentials=(config['SMTP_USERNAME'], config['SMTP_PASSWORD']),
        secure=()
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(complex_formatter)

    # logging.config.dictConfig(yaml.load(file(os.path.join(app.config['BASE_DIR'], '../logging.yaml'),'r')))
    flask_cors_logger = logging.getLogger('flask_cors')
    flask_cors_logger.level = logging.CRITICAL

    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.ERROR)

    loggers = [app.logger, flask_cors_logger, sqlalchemy_logger, logging.getLogger('root')]
    for logger in loggers:
        logger.addHandler(file_handler)
        if not app.debug:
            logger.addHandler(mail_handler)


def create_app():
    """Create an application instance."""
    cfg = os.path.join(os.getcwd(), 'config.py') if os.path.exists('config.py') else os.path.join(os.getcwd(), 'mopa/config.py')

    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    app.config['JSON_PRETTYPRINT_REGULAR'] = False
    app.config.from_pyfile(cfg)
    setup_logging(app)

    # initialize extensions
    db.init_app(app)
    reggie.init_app(app)
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
