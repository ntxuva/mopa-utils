# -*- coding: utf-8 -*-
"""
    mopa.views
    ----------

    Contains the RESTful end points for the app
"""
from flask import Flask, Markup, abort, escape, request, render_template, \
                    jsonify, redirect, Response, make_response, current_app, \
                    Blueprint, flash, g, session, send_from_directory

import datetime
from time import strptime, strftime
from urllib import quote_plus as urlquote
import requests
from logging import getLogger
import json
from functools import update_wrapper
from os import listdir
from os.path import isfile

# Import module models
from mopa.infrastructure import *
from mopa.models import *
import mopa.config as config

bp = api = Blueprint('api', __name__)
logger  = getLogger(__name__)


@api.errorhandler(404)
def not_found(error):
    # Setup HTTP error handling
    return render_template('404.html'), 404

@api.route('/')
def index():
    context = {
        "body": "Hello World!",
        "name": "Mopa"
    }
    return "Hello Mopa", 200

@api.route("/receive-sms", methods=["GET", "POST"])
def receive_sms():
    """End point used by valter to post SMS to us"""
    sms = {
        "from": "",
        "to"  : "",
        "text": ""
    }

    if request.method == "GET":
        sms["from"] = request.args.get("from", "")
        sms["to"]   = request.args.get("to", "")
        sms["text"] = request.args.get("text", "").encode('ascii', errors='backslashreplace')
    elif request.method == "POST":
        sms["from"] = request.form.get("from", "")
        sms["to"]   = request.form.get("to", "")
        sms["text"] = request.form.get("text", "").encode('ascii', errors='backslashreplace')

    if not sms["from"] or not sms["to"] or not sms["text"]:
        logger.error('Received sms in wrong format: ' + (sms["text"] if sms["text"] else " No text in message"))
        abort(400)  # bad request

    db_sms = SMS(direction="I",
                    text=sms["text"],
                    sent_by=sms["from"],
                    sent_to="Mopa")
    Uow.add(db_sms)
    Uow.commit()

    """Right now incoming SMS are only for surveys so check sms for answer
        of survey"""
    sms_answer_parts = sms["text"].split("|")
    if (len(sms_answer_parts) == 1 and
            sms_answer_parts[0].lower() in SMS_VALID_ANSWERS):
        # Group survey answer
        today_survey = Survey.todays()
        if today_survey:
            answer = SurveyAnswer(today_survey.survey_id,
                                    sms_answer_parts[0],
                                    sms["from"],
                                    db_sms.id,
                                    survey_key=today_survey.id)
            Uow.add(answer)
            Uow.commit()
            SMS.static_send(sms["from"], SMS_THANK_YOU)
        else:
            SMS.static_send(sms["from"], SMS_INVALID_FEEDBACK)
    elif (len(sms_answer_parts) == 2 and is_int(sms_answer_parts[0]) and
            sms_answer_parts[1] in SMS_VALID_ANSWERS):
        # Single survey answer
        survey = Survey.get_by_id(sms_answer_parts[0])
        if not survey:
            SMS.static_send(sms["from"], SMS_INVALID_FEEDBACK)
        else:
            answer = SurveyAnswer(survey.survey_id,
                                    sms_answer_parts[1],
                                    sms["from"],
                                    db_sms.id,
                                    survey_key=survey.id)
            Uow.add(answer)
            Uow.commit()
            SMS.static_send(sms["from"], SMS_THANK_YOU)
    else:
        SMS.static_send(sms["from"], SMS_INVALID_FEEDBACK)

    return "Ok", 200

@api.route("/survey", methods=["GET", "POST"])
def survey():
    if request.method == "GET":
        return Response(json.dumps(Survey.get_stats(), cls=CustomJSONEncoder))

    elif request.method == "POST":
        survey_data = {
            "district":      "",
            "neighbourhood": "",
            "point":         "",
            "question_id":   "",
            "question":      ""
        }
        survey_data["district"] = request.form.get("district", "")
        survey_data["neighbourhood"] = \
            request.form.get("neighbourhood", "")
        survey_data["point"] = request.form.get("point", "")
        survey_data["question"] = escape(request.form.get("question", ""))

        to = request.form.get("to", "")

        if(
            not survey_data["district"] or
            not survey_data["neighbourhood"] or
            not survey_data["point"] or
            not survey_data["question"] or
            not to
        ):
            abort(400)  # bad request

        survey = Survey(survey_type="I",
                        district=survey_data["district"],
                        neighbourhood=survey_data["neighbourhood"],
                        point=survey_data["point"],
                        question=survey_data["question"])

        Uow.add(survey)
        Uow.commit()

        sms = SMS.static_send(to,
                                survey_data["question"] + " responda " +
                                survey.survey_id + "| s ou n")
        survey.question_sms = sms

        Uow.add(sms)

        Uow.commit()

        return "Ok", 200

@api.route("/critical-points", methods=["GET"])
def critical_points():
    answers = Survey.get_all()
    the_answers = []
    for answer in answers:
        monitor = Location.i().get_monitor_by_phone(answer["sent_to"])
        if monitor:
            point = Location.i().get_monitor_point(monitor["id"])
            if point:
                answer["name"] = point.get('name', "")
                answer["location"] = point.get('location', "")
                answer["geo_location"] = point.get('geo_location', "")
                answer["neighbourhood"] = point.get('neighbourhood', "")
                answer["district"] = point.get('district', "")
        del answer["answered_by"]
        the_answers.append(answer)

    return Response(json.dumps(the_answers, cls=CustomJSONEncoder))

@api.route("/critical-points/<_date>", methods=["GET"])
def critical_points_by_day(_date):
    answers = Survey.get_day_answers(_date)
    for answer in answers:
        monitor = Location.i().get_monitor_by_phone(answer["sent_to"])
        point = Location.i().get_monitor_point(monitor["id"])
        if point:
            answer["name"] = point.get('name', "")
            answer["location"] = point.get('location', "")
            answer["geo_location"] = point.get('geo_location', "")
            answer["neighbourhood"] = point.get('neighbourhood', "")
            answer["district"] = point.get('district', "")

        del answer["answered_by"]
        del answer["created_at"]

    return Response(json.dumps(answers, cls=CustomJSONEncoder))

@api.route("/reports/", methods=["GET"], defaults={'year': date.today().year, 'month': date.today().month, 'day': date.today().day})
@api.route("/reports/<year>/<month>/<day>", methods=["GET"])
def get_reports(year, month, day):
    logger.info("%s %s %s" % (year, month, day))
    file_name = "relatorio-diario-{0}_{1:02d}_{2:02d}.pdf".format(int(year), int(month), int(day))
    if file_name:
        return send_from_directory(config.REPORTS_DIR, file_name, as_attachment=True)

    files = [f for f in listdir(config.REPORTS_DIR) if isfile(os.path.join(config.REPORTS_DIR, f))]
    return Response(json.dumps(files, cls=CustomJSONEncoder))
