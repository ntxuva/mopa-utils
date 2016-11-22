# -*- coding: utf-8 -*-

import os
import re
import pytz
from os.path import join, dirname
from dotenv import load_dotenv, find_dotenv


def cheap_dot_env(path):
    if os.path.exists('.env'):
        # print('Importing environment from .env...')
        for line in open(path):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]

BASE_DIR = APP_ROOT = os.path.abspath(os.path.dirname(__file__))

# Admin Emails
ADMINS = map(lambda x: x.strip(), os.getenv('ADMINS', 'admin@xample.com').rsplit(','))

APP_NAME = 'Mopa'

# Timezone Settings
TIMEZONE = 'Africa/Harare'
TZ = pytz.timezone(TIMEZONE)

# We named the file env.ini instead of .env because google app engine doesn't
# support uploading dot files
dotenv_path = join(APP_ROOT, '../.env')
load_dotenv(dotenv_path)

# Support multiple environments
# set the config file based on current environment
APP_ENV = os.getenv('APP_ENV', 'development')

if APP_ENV == 'development':
    DEBUG = True  # General debug mode
    DEBUG_LOG = True  # causes all errors to also be saved to a debug.log
    DEBUG_DISPLAY = False  # controls whether debug messages are shown inside the HTML of pages or no
    SCRIPT_DEBUG = True  # SCRIPT_DEBUG is a related constant that will force WordPress to use the "dev" versions of core CSS and JavaScript files rather than the minified versions that are normally loaded
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    WTF_CSRF_ENABLED = False
elif APP_ENV == 'staging':
    DEBUG = True
    DEBUG_LOG = True
    DEBUG_DISPLAY = False
    SCRIPT_DEBUG = False
elif APP_ENV == 'production':
    DEBUG = False
    DEBUG_LOG = False
    DEBUG_DISPLAY = False
    SCRIPT_DEBUG = False


# DB settings
DB_NAME = os.getenv('DB_NAME', 'db')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
# @see: https://mathiasbynens.be/notes/mysql-utf8mb4
DB_CHARSET = 'utf8mb4'
DB_COLLATE = 'utf8mb4_unicode_ci'
DB_PREFIX = os.getenv('DB_PREFIX', 'mopa_')

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://%s:%s@%s:%s/%s" % (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
SQLALCHEMY_POOL_RECYCLE = 28790 # must be lower than MySQL wait_timeout = 28800
DATABASE_CONNECT_OPTIONS = {}


# Email
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT', 25)
SMTP_USE_TLS = bool(os.getenv('SMTP_USE_TLS', "false"))
SMTP_USE_SSL = bool(os.getenv('SMTP_USE_SSL', "false"))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_DEFAULT_NAME = 'Mopa'
EMAIL_DEFAULT_SENDER = 'info@mopa.co.mz'
EMAIL_TEMPLATES_DIR = join(APP_ROOT, '/templates/email/')

# Authentication Unique Keys and Salts
CSRF_ENABLED = True

SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
API_KEY = os.environ.get('API_KEY', 'local')
CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY', 'secret')
WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'secret')


# App
REPORTS_DIR = os.path.join(BASE_DIR, 'data/reports')

# SMS Settings
SC_SMS_END_POINT = os.getenv('SC_SMS_END_POINT', '')
UX_SMS_END_POINT = os.getenv('UX_SMS_END_POINT', '')
SMS_INTRO = "MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao."
SMS_THANK_YOU = "A sua resposta foi recebida. Obrigado pelo seu contributo."
SMS_NO_FEEDBACK_RECEIVED = "Lamentamos nao ter recebido o seu contributo, se o tiver enviado, por favor entre em contacto com a Livaningo, caso contrario pode envia-lo agora."
SMS_INVALID_FEEDBACK = "O seu contributo nao foi reconhecido. Para algum problema, por favor contacte o MOPA."
SMS_VALID_ANSWERS = ["yes", "y", "sim", "s", "nao", "n", "no"]
SMS_UPDATE_NOTIFICATION = "Caro cidadao, o problema reportado por si: [problem_id] foi actualizado. O seu novo estado: [new_status] .Obrigado pelo seu contributo. Mopa"
SMS_NEW_ISSUE_NOTIFICATION = "Novo problema reportado no mopa: [problem_type] - [description] em [district] [neighbourhood] [location_name]"
NEIGHBOURHOODS_JSON_PATH = "static/neighbourhoods-live.json"

# API Settings
OPEN311_BASE_URL = 'http://mopa.co.mz/georeport/v2/'

OPEN311_RESPONSE_FORMATS = {
    'xml':  'xml',
    'json': 'json'
}

OPEN311_END_POINTS = {
    'discovery'	: OPEN311_BASE_URL + 'discovery',
    'requests'	: OPEN311_BASE_URL + 'requests',
    'services'	: OPEN311_BASE_URL + 'services',
    'tokens'	: OPEN311_BASE_URL + 'tokens',
    'locations'	: OPEN311_BASE_URL + 'locations'
}

OPEN311_PHONE_KEY = os.getenv('OPEN311_PHONE_KEY', 'OPEN311_PHONE_KEY')
UX_SMS_API_KEY = os.getenv('UX_SMS_API_KEY', '')

DAILY_REPORT_TO = map(lambda x: x.strip(), os.getenv('DAILY_REPORT_TO', 'admin@xample.com').rsplit(','))
DAILY_REPORT_CC = map(lambda x: x.strip(), os.getenv('DAILY_REPORT_CC', 'admin@xample.com').rsplit(','))
DAILY_ENQUIRY_REPORT_TO = DAILY_REPORT_CC
WEEKLY_REPORT_TO = DAILY_REPORT_CC
