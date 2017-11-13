# -*- coding: utf-8 -*-
"""
    mopa.views
    ----------

    Contains the RESTful end points for the app
"""
from flask import Flask, Markup, abort, escape, request, render_template, \
                    jsonify, redirect, Response, make_response, current_app, \
                    Blueprint, flash, g, session, send_from_directory

import json
from os import listdir
from os.path import isfile

from retry import retry
from retry.api import retry_call
import requests
from requests.exceptions import ConnectTimeout

# Import module models
from mopa.infrastructure import *
from mopa.models import *
import mopa.config as config


bp = api = Blueprint('api', __name__)


@api.errorhandler(404)
def not_found(error):
    # Setup HTTP error handling
    return render_template('404.html'), 404


@api.route('/')
def index():
    return "Hello Mopa", 200


@api.route("/receive-sms", methods=["GET", "POST"])
def receive_sms():
    """End point used by valter to post SMS to us"""
    incoming_sms = {
        "from": "",
        "to"  : "",
        "text": ""
    }
    outgoing_sms = config.SMS_INVALID_FEEDBACK

    if request.method == "GET":
        incoming_sms["from"] = request.args.get("from", "")
        incoming_sms["to"]   = request.args.get("to", "")
        incoming_sms["text"] = request.args.get("text", "").encode('ascii', errors='backslashreplace')

    if request.method == "POST":
        incoming_sms["from"] = request.form.get("from", "")
        incoming_sms["to"]   = request.form.get("to", "")
        incoming_sms["text"] = request.form.get("text", "").encode('ascii', errors='backslashreplace')

    if not incoming_sms["from"] or not incoming_sms["to"] or not incoming_sms["text"]:
        current_app.logger.error('Received sms in wrong format: ' + (incoming_sms["text"] if incoming_sms["text"] else " No text in message"))
        abort(400)  # bad request

    stored_incoming_sms = SMS(direction="I", text=incoming_sms["text"], sent_by=incoming_sms["from"], sent_to="Mopa")
    Uow.add(stored_incoming_sms)
    Uow.commit()

    monitor_phone_numbers = [] # TODO(dareenzo): replace this fake with read data

    if incoming_sms['from'] in monitor_phone_numbers:
        incoming_sms_parts = incoming_sms["text"].split("|")

        if len(incoming_sms_parts) == 1 and incoming_sms_parts[0].lower() in config.SMS_VALID_ANSWERS:
            # Group survey answer
            today_survey = Survey.todays()

            if today_survey:
                answer = SurveyAnswer(today_survey.survey_id, incoming_sms_parts[0], incoming_sms["from"], stored_incoming_sms.id, survey_key=today_survey.id)
                Uow.add(answer)
                Uow.commit()
                outgoing_sms = config.SMS_THANK_YOU

        elif len(incoming_sms_parts) == 2 and is_int(incoming_sms_parts[0]) and incoming_sms_parts[1] in config.SMS_VALID_ANSWERS:
            # Single survey answer
            _survey = Survey.get_by_id(incoming_sms_parts[0])

            if _survey:
                answer = SurveyAnswer(_survey.survey_id, incoming_sms_parts[1], incoming_sms["from"], stored_incoming_sms.id, survey_key=_survey.id)
                Uow.add(answer)
                Uow.commit()
                outgoing_sms = config.SMS_THANK_YOU

        SMS.static_send(incoming_sms["from"], outgoing_sms)
    else:
        try:
            r = retry_call(requests.put, fargs=[config.OPEN311_END_POINTS['reopen'] + '/' + incoming_sms['from'] + '.' + config.OPEN311_RESPONSE_FORMATS['json']], exceptions=ConnectTimeout, tries=3)
            if r.status_code == 200:
                issue = r.json()
                SMS.static_send(incoming_sms["from"], config.SMS_ISSUE_REOPEN_SUCCESS % (issue.get('service_request_id', default)))
            else:
                SMS.static_send(incoming_sms["from"], config.SMS_ISSUE_REOPEN_FAIL)
        except:
            pass

    return "Ok", 200


@api.route("/survey", methods=["GET", "POST"])
def survey():
    if request.method == "GET":
        return Response(json.dumps(Survey.get_stats(), cls=CustomJSONEncoder))

    if request.method == "POST":
        survey_data = {
            "district":      request.form.get("district", ""),
            "neighbourhood": request.form.get("neighbourhood", ""),
            "point":         request.form.get("point", ""),
            "question_id":   "",
            "question":      escape(request.form.get("question", ""))
        }

        to = request.form.get("to", "")

        if(
            not survey_data["district"] or
            not survey_data["neighbourhood"] or
            not survey_data["point"] or
            not survey_data["question"] or
            not to
        ):
            abort(400)  # bad request

        _survey = Survey(survey_type="I", district=survey_data["district"], neighbourhood=survey_data["neighbourhood"],
                         point=survey_data["point"], question=survey_data["question"])

        Uow.add(survey)
        Uow.commit()

        sms = SMS.static_send(to, survey_data["question"] + " responda " + _survey.survey_id + "| s ou n")
        _survey.question_sms = sms

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


@api.route("/critical-points/<day>", methods=["GET"])
def get_critical_points_by_day(day):
    answers = Survey.get_day_answers(day)
    for answer in answers:
        monitor = Location.i().get_monitor_by_phone(answer["sent_to"])
        point = Location.i().get_monitor_point(monitor["id"])
        if point:
            answer["name"] = point.get('name', "")
            answer["location"] = point.get('location', "")
            answer["geo_location"] = point.get('geo_location', "")
            answer["neighbourhood"] = point.get('neighbourhood', "")
        del answer["answered_by"]
        del answer["created_at"]

    return Response(json.dumps(answers, cls=CustomJSONEncoder))


@api.route("/reports/", methods=["GET"], defaults={'district': 'kamaxaquene', 'year': date.today().year, 'month': date.today().month, 'day': date.today().day})
@api.route("/reports/<district>/<year>/<month>/<day>", methods=["GET"])
def get_reports(district, year, month, day):
    current_app.logger.info("%s %s %s" % (year, month, day))
    file_name = "relatorio-diario-{0}-{1}_{2:02d}_{3:02d}.pdf".format(district, int(year), int(month), int(day))
    if file_name:
        return send_from_directory(config.REPORTS_DIR, file_name, as_attachment=True)

    files = [f for f in listdir(config.REPORTS_DIR) if isfile(os.path.join(config.REPORTS_DIR, f))]
    return Response(json.dumps(files, cls=CustomJSONEncoder))
