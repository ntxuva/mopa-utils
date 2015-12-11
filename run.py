#!/bin/python
# -*- coding: utf-8 -*-
from mopa import app, tasks, models, views, common, constants
from threading import Thread
import logging
import config
from logging.handlers import RotatingFileHandler, SMTPHandler

if __name__ == "__main__":

    tasks.send_weekly_report()
    """
    # Setup Logging
    # Rotating log file handling
    handler = RotatingFileHandler("mopa/logs/mopa.log", maxBytes=10000, backupCount=1)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Email log handling
    if not app.debug:
        mail_handler = SMTPHandler((constants.GMAIL_SERVER, constants.GMAIL_PORT),
                                   constants.GMAIL_USER,
                                   config.ADMINS,
                                   'Mopa Failed',
                                   credentials=(constants.GMAIL_USER, constants.GMAIL_PASSWORD),
                                   secure=())
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # Setup DB - Might delete your tables watch out
    # models.setup_models()

    # Setup tasks
    tasks.setup_tasks()

    # Thread for running tasks only
    t = Thread(target=tasks.run_scheduler)
    t.start()

    # Setup and run api
    views.setup_api()
    app.run(debug=config.DEBUG,
            use_reloader=config.DEBUG,  # This must be set to false in production or scheduled taks will run 2x. But keep it True when debugging
            host="0.0.0.0",
            port=int(5000),
            threaded=True)
    """
