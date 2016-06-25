# -*- coding: utf-8 -*-
"""
    mopa.constants
    --------------

    Contains system wide constants
"""
import pytz
import os

# Timezone Settings
TZ = pytz.timezone('Africa/Harare')
# TZ = pytz.timezone('Europe/Lisbon')

# Reports Dir
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# SMS Settings
SMS_END_POINT = ""
SMS_INTRO = "MOPA - O seu ponto critico tem algum problema neste momento? Responda S para sim e N para Nao."
SMS_THANK_YOU = "A sua resposta foi recebida. Obrigado pelo seu contributo."
SMS_NO_FEEDBACK_RECEIVED = "Lamentamos nao ter recebido o seu contributo, se o tiver enviado, por favor entre em contacto com a Livaningo, caso contrario pode envia-lo agora."
SMS_INVALID_FEEDBACK = "O seu contributo nao foi reconhecido. Para algum problema, por favor contacte o MOPA."
SMS_VALID_ANSWERS = ["yes", "y", "sim", "s", "nao", "n", "no"]
SMS_UPDATE_NOTIFICATION = "Caro cidadao, o problema reportado por si: [problem_id] foi actualizado. O seu novo estado: [new_status] .Obrigado pelo seu contributo. Mopa"
SMS_NEW_ISSUE_NOTIFICATION = "Novo problema reportado no mopa: [problem_type] - [description] em [district] [neighbourhood] [location_name]"
NEIGHBOURHOODS_JSON_PATH = "static/neighbourhoods-live.json"

# API Settings
API_BASE_URL = 'http://mopa.co.mz/georeport/v2/'

API_RESPONSE_FORMATS = {
    'xml':  'xml',
    'json': 'json'
}

API_END_POINTS = {
    'discovery'	: API_BASE_URL + 'discovery',
    'requests'	: API_BASE_URL + 'requests',
    'services'	: API_BASE_URL + 'services',
    'tokens'	: API_BASE_URL + 'tokens',
    'locations'	: API_BASE_URL + 'locations'
}

API_PHONE_KEY = 666554

# Mail Settings
GMAIL_SERVER = 'smtp.gmail.com'
GMAIL_PORT = 587
GMAIL_USER = ""
GMAIL_PASSWORD = ""

DAILY_REPORT_TO = ['admin@localhost']
DAILY_REPORT_CC = ['admin@localhost']
DAILY_ENQUIRY_REPORT_TO = DAILY_REPORT_CC
WEEKLY_REPORT_TO = DAILY_REPORT_CC
