# -*- coding: utf-8 -*-
"""
    mopa.views
    ----------

    Contains the RESTful end points for the app
"""
from flask import Flask, Markup, abort, escape, request, render_template, \
                    jsonify, redirect, Response, make_response, current_app, \
                    Blueprint, flash, g, session, send_from_directory

import pandas as pd
import dateutil.parser
import locale

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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
    context = {
        "body": "Hello World!",
        "name": "Mopa"
    }
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
                answer = SurveyAnswer(today_survey.survey_id,  incoming_sms_parts[0], incoming_sms["from"], stored_incoming_sms.id, survey_key=today_survey.id)
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
            r = retry_call(requests.put, fargs=[config.OPEN311_END_POINTS['requests'] + '/' + incoming_sms['from'] + '.' + config.OPEN311_RESPONSE_FORMATS['json']], exceptions=ConnectTimeout, tries=3)
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


@api.route("/reports/", methods=["GET"], defaults={'district' : 'kamaxaquene', 'year': date.today().year, 'month': date.today().month, 'day': date.today().day})
@api.route("/reports/<district>/<year>/<month>/<day>", methods=["GET"])
def get_reports(district, year, month, day):
    current_app.logger.info("%s %s %s" % (year, month, day))
    file_name = "relatorio-diario-{0}-{1}_{2:02d}_{3:02d}.pdf".format(district, int(year), int(month), int(day))
    if file_name:
        return send_from_directory(config.REPORTS_DIR, file_name, as_attachment=True)

    files = [f for f in listdir(config.REPORTS_DIR) if isfile(os.path.join(config.REPORTS_DIR, f))]
    return Response(json.dumps(files, cls=CustomJSONEncoder))

@api.route("/monthly-report", methods=["GET"])
def get_stats():
    today = datetime.utcnow()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=1)
    lastMonth_first = lastMonth.replace(day=1)

    all_reports = pd.read_json('http://mopa.co.mz/georeport/v2/requests.json')
    all_reports['requested_datetime'] = pd.to_datetime(all_reports['requested_datetime'])
    all_reports['requested_month'] = all_reports['requested_datetime'].apply(lambda t: t.strftime('%Y-%m'))
    all_reports = translate_column_names(all_reports)

    reports = pd.read_json('http://mopa.co.mz/georeport/v2/requests.json?start_date='  + lastMonth_first.strftime('%Y-%m-%d') + '&end_date=' + lastMonth.strftime('%Y-%m-%d') + '&phone_key=666554')

    reports['requested_datetime'] = pd.to_datetime(reports['requested_datetime'])
    reports['updated_datetime'] = pd.to_datetime(reports['updated_datetime'])
    reports['requested_month'] = reports['requested_datetime'].apply(lambda t: t.strftime('%y/%m'))
    reports['response_time'] = (reports['updated_datetime'] - reports['requested_datetime']).dt.days

    districts = pd.read_csv(os.path.join(config.BASE_DIR, 'static/neighbourhoods.csv'))
    reports = reports.merge(districts, how='left', left_on='neighbourhood', right_on='neighbourhood')

    reports = translate_column_names(reports)

    # prepare tables

    table_service_per_month = pd.crosstab(reports['Categoria'], reports['Estado'])
    table_service_per_month['Total'] = table_service_per_month.sum(axis = 1)
    table_service_per_month = table_service_per_month.to_html()

    table_problems_per_district = pd.crosstab(reports['Categoria'], reports['Distrito'])
    table_problems_per_district['Total'] = table_problems_per_district.sum(axis = 1) # sum rows
    table_problems_per_district = table_problems_per_district.to_html()

    table_response_time_per_service = reports['response_time']\
        .groupby(reports['Categoria'])\
        .agg({'Número de problemas' : np.size, 'Tempo medio de resposta (dias)' : np.mean})\
        .to_html(float_format = '%2.2f')

    table_unique_citizens_per_district = reports\
        .pivot_table(index='Categoria', columns='Distrito', values='phone',
                     fill_value=0,
                     aggfunc = pd.Series.nunique)\
        .to_html()

    ## prepare figures

    fig0 = plt.figure()
    image0_table = pd.crosstab(all_reports['Mes'], all_reports['Categoria'])
    image0_table.plot(kind='bar')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot0.png'), dpi=68)

    fig1_1 = plt.figure()
    ax1_1 = fig1_1.add_subplot(111)
    image1_table = reports['Distrito'].value_counts()
    image1_table.plot(kind='pie', autopct='%1.0f%%', pctdistance=0.9, labeldistance=1.2)
    plt.tight_layout()
    ax1_1.set_aspect('equal')
    plt.ylabel('')
    plt.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot1_1.png'), dpi=65)

    fig1_2 = plt.figure()
    ax1_2 = fig1_2.add_subplot(111)
    image2_table = reports['Categoria'].value_counts()
    image2_table.plot(kind='pie', autopct='%1.0f%%', pctdistance=0.9, labeldistance=1.2)
    ax1_2.set_aspect('equal')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot1_2.png'), dpi=65)

    fig1_3 = plt.figure()
    ax1_3 = fig1_3.add_subplot(111)
    image2_table = reports['Estado'].value_counts()
    image2_table.plot(kind='pie', autopct='%1.0f%%', pctdistance=0.9, labeldistance=1.2)
    ax1_3.set_aspect('equal')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot1_3.png'), dpi=65)

    fig3 = plt.figure()
    image3_table = pd.crosstab(reports['Categoria'], reports['requested_datetime'].dt.weekday)
    image3_table.columns = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
    sns.heatmap(image3_table, annot=True, linewidths=.5, annot_kws={"size": 8}, fmt='g', cmap='Reds', cbar=False)
    plt.tight_layout()
    fig3.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot3.png'), dpi=70)

    fig4 = plt.figure()
    image4_table = pd.crosstab(reports['Categoria'], reports['requested_datetime'].dt.hour)
    sns.heatmap(image4_table, annot=True, linewidths=.5, annot_kws={"size": 8}, fmt='g', cmap='Reds', cbar=False)
    plt.xlabel('Horas')
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig4.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot4.png'), dpi=65)

    fig5 = plt.figure()
    image5_table = pd.crosstab(reports['Categoria'], reports['updated_datetime'].dt.hour+2)
    _ = sns.heatmap(image5_table, annot=True, linewidths=.5, annot_kws={"size": 8}, fmt='g', cmap='Reds', cbar=False)
    plt.yticks(rotation=0)
    plt.xlabel('Horas')
    plt.tight_layout()
    fig5.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot5.png'), dpi=65)

    fig6 = plt.figure()
    ax6 = fig6.add_subplot(111)
    image6_values =[reports['status_notes'].count(), len(reports.index)]
    image6_labels = ['Esclarecimento do CMM', 'Nenhum esclarecimento do CMM']
    plt.pie(image6_values, autopct='%1.0f%%', pctdistance=0.9)
    ax6.set_aspect('equal')
    plt.legend(labels = image6_labels, loc="best")
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/report_images/plot6.png'), dpi=80)

    locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')

    # Generate PDF
    context = {
        'today': today.strftime('%d-%m-%Y'),
        'month': lastMonth.strftime('%B de %Y'),
        'table1': table_service_per_month,
        'table2': table_problems_per_district,
        'table3': table_response_time_per_service,
        'table4': table_unique_citizens_per_district,
        'static': os.path.join(config.BASE_DIR, 'templates') + '/'
    }

    f_name = 'relatorio-mensal-' + '-' + today.strftime('%Y_%m_%d') + '.pdf'
    generate_pdf('monthly_report.html', context, f_name)

    return "Report successfully generated for %s." % lastMonth.strftime('%B of %Y'), 200

def translate_column_names(df):
    df.rename(columns={'service_notice' : 'Estado', 'district' : 'Distrito', 'service_name' : 'Categoria', 'requested_month' : 'Mes'}, inplace = True)
    return df
