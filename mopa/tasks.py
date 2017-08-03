# -*- coding: utf-8 -*-
"""
    mopa.tasks
    ----------

    Contains the scheduled tasks definition
"""
from __future__ import unicode_literals, print_function
import os
import sys

from datetime import datetime, date, timedelta
from dateutil.parser import parse
import requests
from requests.exceptions import ConnectTimeout

from retry.api import retry_call
import traceback
from flask import Blueprint, current_app, request, abort
from sqlalchemy.exc import IntegrityError, DisconnectionError

from slugify import slugify

import pandas as pd
import dateutil.parser
import locale
import warnings

import matplotlib
matplotlib.use('Agg', warn=False) # tell matplot not to use XWindows

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import mopa.config as config
from mopa.infrastructure import (
    Location, xstr, snake_case, remove_accents, get_requests, generate_pdf, send_mail, truncate
)
from mopa.models import Uow, SMS, Survey, Report


bp = tasks = Blueprint('tasks', __name__)


@tasks.before_request
def before_request():
    """Checks if API_KEY is valid"""
    api_key = request.headers.get('API_KEY', None)
    if not api_key or api_key != current_app.config['API_KEY']:
        abort(403)  # Forbidden / Not Authorized


@tasks.route('/send-weekly-report/<regex("\d{4}-\d{2}-\d{2}"):today>')
@tasks.route('/send-weekly-report')
def send_weekly_report(today=None):
    """Task to run weekly for report"""

    today = date.today() if today is None else datetime.strptime(today, '%Y-%m-%d')
    start_date = today + timedelta(days=-7)
    end_date = today

    old_start_date = start_date + timedelta(days=-7)
    old_end_date = start_date

    # Get requests
    default = ''
    requests_list = []

    for _request in get_requests(start_date, end_date, True):
        location = Location.i().guess_location(_request)

        del _request['zipcode']
        del _request['lat']
        del _request['long']

        district = location['district']
        neighbourhood = location['neighbourhood']
        location_name = location['location_name']

        report = Report()
        report.id = xstr(_request['service_request_id'])
        report.district = district
        report.neighbourhood = neighbourhood
        report.location_name = location_name
        report.nature = xstr(_request['service_name'])
        report.requested_datetime = (xstr(_request['requested_datetime'])[0:10] + " " + xstr(_request['requested_datetime'])[11:19])
        report.updated_datetime = (xstr(_request['updated_datetime'])[0:10] + " " + xstr(_request['updated_datetime'])[11:19])
        report.type = xstr(_request['service_name'])
        report.status = xstr(_request['service_notice'])
        report.status_notes = xstr(_request.get('status_notes', ''))

        Uow.add(report)
        try:
            Uow.commit()
        except IntegrityError:
            Uow.rollback()
        except Exception, ex:
            Uow.rollback()
            current_app.logger.error("Error While Inserting Report in DB\n" + traceback.format_exc())

    # Report by State
    # ---------------
    estados_report_rows = Report.get_summary_report(start_date, end_date, old_start_date, old_end_date)

    # calculate totals for states
    total_occurencies = 0
    total_pct = 0
    total_tempo_medio_resolucao = 0
    total_variacao = 0

    for estado in estados_report_rows:
        total_occurencies += estado["no_occorencias"]
        total_pct += estado["pct_do_total"]
        total_tempo_medio_resolucao += estado["tempo_medio_resolucao"]
        total_variacao += estado.get("variacao") if estado.get("variacao") else 0

    estados_report_rows.append({
        'type': 'TOTAL',
        'no_occorencias': total_occurencies,
        'pct_do_total': total_pct,
        'tempo_medio_resolucao': total_tempo_medio_resolucao,
        'variacao': total_variacao
    })

    # Report by District
    # ------------------
    district_rows = Report.get_summary_by_district_report(start_date, end_date, old_start_date, old_end_date)

    # Calculate totals per district
    district_totals = {}
    district_names = []
    districts = {}

    for row in district_rows:
        district_names.append(row["district"])

    district_names = list(set(district_names))  # remove duplicates

    for row in district_rows:
        if not district_totals.get(row["district"]):
            district_totals[row["district"]] = {
                "no_occorencias": 0,
                "pct_do_total": 0,
                "tempo_medio_resolucao": 0,
                "variacao": 0
            }

        district_totals[row["district"]]["no_occorencias"] += row["no_occorencias"]
        district_totals[row["district"]]["pct_do_total"] += row["pct_do_total"]
        district_totals[row["district"]]["tempo_medio_resolucao"] += row["tempo_medio_resolucao"]
        district_totals[row["district"]]["variacao"] += row.get("variacao", 0)

    for district in district_names:
        districts[district] = {
            "name": district,
            "totals": district_totals[district],
            "rows": []
        }

        for row in district_rows:
            if row["district"] == district:
                districts[district]["rows"].append(row)

    # Tiago Report
    # ------------
    t_report_rows = Report.get_by_problem(start_date, end_date)
    t_neighbourhood_names = []
    t_neighbourhoods = {}
    problem_types = [
        u"Tchova não passou",
        u"Contentor está cheio",
        u"Amontoado de lixo",
        u"Lixo fora do contentor",
        u"Lixo na vala de drenagem",
        u"Camião não passou",
        u"Contentor a Arder",
        u"Entulho na rua",
        u"Ramos no chão"
    ]

    problem_images = map(lambda x: remove_accents(x).lower().replace(' ', '_'), problem_types)

    for row in t_report_rows:
        t_neighbourhood_names.append(row["bairro"])

    t_neighbourhood_names = list(set(t_neighbourhood_names))

    for neighbourhood in t_neighbourhood_names:
        t_neighbourhoods[neighbourhood] = {
            "name": neighbourhood,
            "rows": []
        }

        for row in t_report_rows:
            if row["bairro"] == neighbourhood:
                t_neighbourhoods[neighbourhood]["rows"].append({
                    "problema": row.get("problema", "-"),
                    "registado": row.get("registado", 0),
                    "em_processo": row.get("em_processo", 0),
                    "resolvido": row.get("resolvido", 0),
                    # "arquivado": row.get("arquivado", 0),
                    "invalido": row.get("invalido", 0),
                    "total": row.get("total", 0)
                })

    for neighbourhood in t_neighbourhood_names:
        neighbourhood_problems = []

        for row in t_neighbourhoods[neighbourhood]["rows"]:
            neighbourhood_problems.append(row["problema"])

        for problem_type in problem_types:
            if problem_type not in neighbourhood_problems:
                t_neighbourhoods[neighbourhood]["rows"].append({
                    "problema": problem_type,
                    "registado": 0,
                    "em_processo": 0,
                    "resolvido": 0,
                    # "arquivado": 0,
                    "invalido": 0,
                    "total": 0
                })

        t_neighbourhoods[neighbourhood]["rows"] = sorted(
            t_neighbourhoods[neighbourhood]["rows"],
            key=lambda i: (-1 * i['total'])
        )

    for neighbourhood in t_neighbourhood_names:
        if t_neighbourhoods[neighbourhood]["rows"][0]["total"] > 0:
            t_neighbourhoods[neighbourhood]["most_frequent_problem"] = t_neighbourhoods[neighbourhood]["rows"][0]["problema"]
        else:
            t_neighbourhoods[neighbourhood]["most_frequent_problem"] = None

        t_neighbourhoods[neighbourhood]["rows"] = sorted(t_neighbourhoods[neighbourhood]["rows"], key=lambda i: (-1 * i['resolvido']))

        if t_neighbourhoods[neighbourhood]["rows"][0]["resolvido"] > 0:
            t_neighbourhoods[neighbourhood]["most_solved_problem"] = t_neighbourhoods[neighbourhood]["rows"][0]["problema"]
        else:
            t_neighbourhoods[neighbourhood]["most_solved_problem"] = None

        t_neighbourhoods[neighbourhood]["rows"] = sorted(t_neighbourhoods[neighbourhood]["rows"], key=lambda i: (-1 * i['total']))

    for neighbourhood in t_neighbourhood_names:
        t_neighbourhoods[neighbourhood]["worst_critical_points"] = Report.get_worst_critical_points(neighbourhood, start_date, end_date)

    # Generate PDF
    context = {
        'today': today.strftime('%d-%m-%Y'),
        'sumario': {
            'estados': estados_report_rows,
            'district_names': district_names,
            'districts': districts
        },
        'details': {
            'neighbourhood_names': t_neighbourhood_names,
            'neighbourhoods': t_neighbourhoods
        },
        'icons': dict(zip(problem_types, problem_images)),
        'static': os.path.join(config.BASE_DIR, 'templates') + '/'
    }
    f_name = 'relatorio-semanal-' + today.strftime('%Y_%m_%d') + '.pdf'
    generate_pdf('weekly_report.html', context, f_name)

    # Send mail
    html = '''\
        <html>
            <head></head>
            <body>
            <p>Sauda&ccedil;&otilde;es!<br/><br/>
                Segue em anexo o relat&oacute;rio MOPA<br/><br/>
                Cumprimentos,<br/>
                <em>Enviado automaticamente</em>
            </p>
            </body>
        </html>
            '''
    send_mail(
        config.WEEKLY_REPORT_TO,
        '[MOPA] Relatorio Semanal - ' + today.strftime('%Y-%m-%d'),
        html,
        is_html=True,
        cc=config.DAILY_REPORT_CC,
        sender=(config.EMAIL_DEFAULT_NAME, config.EMAIL_DEFAULT_SENDER),
        attachments=[config.REPORTS_DIR + '/' + f_name]
    )

    return "Ok", 200


@tasks.route('/send-monthly-report')
def send_monthly_report():
    """Task to prepare and send the monthly report"""
    today = datetime.utcnow()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=1)
    lastMonth_first = lastMonth.replace(day=1)

    districts = pd.read_csv(os.path.join(config.BASE_DIR, 'static/neighbourhoods.csv'))

    all_reports = pd.read_json('http://mopa.co.mz/georeport/v2/requests.json?end_date=' + lastMonth.strftime('%Y-%m-%d'))
    all_reports['requested_datetime'] = pd.to_datetime(all_reports['requested_datetime'])
    all_reports['requested_month'] = all_reports['requested_datetime'].apply(lambda t: t.strftime('%Y-%m'))
    all_reports = all_reports.merge(districts, how='left', left_on='neighbourhood', right_on='neighbourhood')
    all_reports = translate_column_names(all_reports)

    reports = pd.read_json('http://mopa.co.mz/georeport/v2/requests.json?start_date='  + lastMonth_first.strftime('%Y-%m-%d') + '&end_date=' + lastMonth.strftime('%Y-%m-%d') + '&phone_key=666554')

    reports['requested_datetime'] = pd.to_datetime(reports['requested_datetime'])
    reports['updated_datetime'] = pd.to_datetime(reports['updated_datetime'])
    reports['requested_month'] = reports['requested_datetime'].apply(lambda t: t.strftime('%y/%m'))
    reports['response_time'] = (reports['updated_datetime'] - reports['requested_datetime']).dt.days
    reports = reports.merge(districts, how='left', left_on='neighbourhood', right_on='neighbourhood')
    reports = translate_column_names(reports)

    # prepare tables

    table_problems_per_district_per_month = pd.crosstab(all_reports['Distrito'], all_reports['Mes'], margins = True)
    table_problems_per_district_per_month = table_problems_per_district_per_month.to_html()

    table_problems_per_month = pd.crosstab(all_reports['Categoria'], all_reports['Mes'], margins = True)
    table_problems_per_month = table_problems_per_month.to_html()

    table_service_per_month = pd.crosstab(reports['Categoria'], reports['Estado'], margins = True)
    table_service_per_month = table_service_per_month.to_html()

    table_problems_per_district = pd.crosstab(reports['Categoria'], reports['Distrito'], margins = True)
    table_problems_per_district = table_problems_per_district.to_html()

    table_response_time_per_service = reports['response_time']\
        .groupby(reports['Categoria'])\
        .agg({'Número de problemas' : np.size, 'Tempo medio de resposta (dias)' : np.mean})\
        .to_html(float_format = '%2.2f')

    table_unique_citizens_per_district = reports\
        .pivot_table(index='Categoria', columns='Distrito', values='phone',
                     fill_value=0,
                     aggfunc = pd.Series.nunique, margins = True)
    table_unique_citizens_per_district = table_unique_citizens_per_district.to_html(float_format = '%d')

    ## prepare figures

    fig0 = plt.figure()
    image0_table = all_reports['Mes'].value_counts().sort_index(ascending = True)
    ax = image0_table.plot(kind='bar')
    plt.xticks(rotation=0)

    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    for bar in ax.patches:
        height = bar.get_height()
        plt.gca().text(bar.get_x() + bar.get_width()/2, bar.get_height() - 100 , str('{:d}'.format(int(height))),
                 ha='center', color='w', fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot0.png'), dpi=300)

    fig00 = plt.figure()
    image0_table = pd.crosstab(all_reports['Mes'], all_reports['Categoria'])
    ax = image0_table.plot()
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot00.png'), dpi=300)

    fig1_1 = plt.figure()
    ax1_1 = fig1_1.add_subplot(111)
    image1_table = reports['Distrito'].value_counts()
    image1_table.plot(kind='pie', autopct='%1.0f%%', pctdistance=0.9, labeldistance=1.2)
    plt.tight_layout()
    ax1_1.set_aspect('equal')
    plt.ylabel('')
    plt.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot1_1.png'), dpi=300)

    fig1_2 = plt.figure()
    ax1_2 = fig1_2.add_subplot(111)
    image2_table = reports['Categoria'].value_counts()
    image2_table.plot(kind='pie', autopct='%1.0f%%', pctdistance=0.9, labeldistance=1.2)
    ax1_2.set_aspect('equal')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot1_2.png'), dpi=300)

    fig1_3 = plt.figure()
    ax1_3 = fig1_3.add_subplot(111)
    image2_table = reports['Estado'].value_counts()
    image2_table.plot(kind='pie', autopct='%1.0f%%', pctdistance=0.9, labeldistance=1.2)
    ax1_3.set_aspect('equal')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot1_3.png'), dpi=300)

    fig3 = plt.figure()
    image3_table = pd.crosstab(reports['Categoria'], reports['requested_datetime'].dt.weekday)
    image3_table.columns = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
    sns.heatmap(image3_table, annot=True, linewidths=.5, annot_kws={"size": 8}, fmt='g', cmap='Reds', cbar=False)
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig3.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot3.png'), dpi=300)

    fig4 = plt.figure()
    image4_table = pd.crosstab(reports['Categoria'], reports['requested_datetime'].dt.hour)
    sns.heatmap(image4_table, annot=True, linewidths=.5, annot_kws={"size": 8}, fmt='g', cmap='Reds', cbar=False)
    plt.xlabel('Horas')
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig4.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot4.png'), dpi=300)

    fig5 = plt.figure()
    image5_table = pd.crosstab(reports['Categoria'], reports['updated_datetime'].dt.hour+2)
    _ = sns.heatmap(image5_table, annot=True, linewidths=.5, annot_kws={"size": 8}, fmt='g', cmap='Reds', cbar=False)
    plt.yticks(rotation=0)
    plt.xlabel('Horas')
    plt.tight_layout()
    fig5.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot5.png'), dpi=300)

    fig6 = plt.figure()
    ax6 = fig6.add_subplot(111)
    image6_values =[reports['status_notes'].count(), len(reports.index)]
    image6_labels = ['Esclarecimento do CMM', 'Nenhum esclarecimento do CMM']
    plt.pie(image6_values, autopct='%1.0f%%', pctdistance=0.9)
    ax6.set_aspect('equal')
    plt.legend(labels = image6_labels, loc="best")
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(os.path.join(config.BASE_DIR, 'static/img/monthly_report/plot6.png'), dpi=300)

    try:
        locale.setlocale(locale.LC_ALL, str('pt_PT.UTF-8'))
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, str('Portuguese_Portugal.1252'))
        except locale.Error:
            warnings.warn("Could not set locale to Portuguese/Portugal. ")

    # Generate PDF
    context = {
        'today': today.strftime('%d-%m-%Y'),
        'month': lastMonth.strftime('%m/%Y'),
        'table_problems_per_month' : table_problems_per_month,
        'table_problems_per_district_per_month' : table_problems_per_district_per_month,
        'table1': table_service_per_month,
        'table2': table_problems_per_district,
        'table3': table_response_time_per_service,
        'table4': table_unique_citizens_per_district,
        'static': os.path.join(config.BASE_DIR, 'templates') + '/'
    }

    f_name = 'relatorio-mensal-' + '-' + today.strftime('%Y_%m_%d') + '.pdf'
    generate_pdf('monthly_report.html', context, f_name)

    html = '''
        <html>
            <head></head>
            <body>
            <p>Sauda&ccedil;&otilde;es!<br/><br/>
                Segue em anexo o relatorio mensal<br/><br/>
                Cumprimentos,<br/>
                <em>Enviado automaticamente</em>
            </p>
            </body>
        </html>
    '''

    send_mail(
        config.WEEKLY_REPORT_TO,
        '[MOPA] Relatorio Mensal - ' + lastMonth.strftime('%B of %Y'),
        html,
        is_html=True,
        cc=config.DAILY_REPORT_CC,
        sender=(config.EMAIL_DEFAULT_NAME, config.EMAIL_DEFAULT_SENDER),
        attachments=[config.REPORTS_DIR + '/' + f_name]
    )

    return "Report successfully generated for %s." % lastMonth.strftime('%B of %Y'), 200

@tasks.route('/send-daily-report/<regex("\d{4}-\d{2}-\d{2}"):today>')
@tasks.route('/send-daily-report')
def send_daily_report(today=None):
    """Task to run the Daily PDF Exporter"""

    today = date.today() if today is None else datetime.strptime(today, '%Y-%m-%d')

    # Get requests
    default = ''
    requests_list = []
    districts = []

    start_date = (today + timedelta(days=-2)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    for _request in get_requests(start_date, end_date, None):

        location = Location.i().guess_location(_request)

        district = location['district']
        districts.append(district.lower())
        neighbourhood = location['neighbourhood']
        location_name = location['location_name']

        requests_list.append({
                'id': xstr(_request['service_request_id']),
                'district': district,
                'neighbourhood': neighbourhood,
                'location_name': location_name,
                'nature': xstr(_request['service_name']),
                'datetime': xstr(_request['requested_datetime'])[0:10] + " " + xstr(_request['requested_datetime'])[11:19],
                'type': xstr(_request['service_name']),
                'status': xstr(_request['service_notice']),
                'status_notes': xstr(_request.get('status_notes', ''))
            })

    # sorting
    requests_list = sorted(requests_list, key=lambda i: (i['district'], i['neighbourhood'], i['nature'], i['datetime']))

    # per district export
    districts = set(districts)

    for district in districts:
        district_requests = filter(lambda x: x['district'].lower() == district, requests_list)

        # Generate PDF
        context = {
            'today': today.strftime('%d-%m-%Y'),
            'requests_list': district_requests,
            'static': os.path.join(config.BASE_DIR, 'templates') + '/'
        }

        f_name = 'relatorio-diario-' + slugify(district) + '-' + today.strftime('%Y_%m_%d') + '.pdf'
        generate_pdf('daily_report.html', context, f_name)

        # Send mail
        html = '''\
            <html>
                <head></head>
                <body>
                <p>Sauda&ccedil;&otilde;es!<br/><br/>
                    Segue em anexo o relat&oacute;rio MOPA<br/><br/>
                    Cumprimentos,<br/>
                    <em>Enviado automaticamente</em>
                </p>
                </body>
            </html>
                '''
        send_mail(
            config.DAILY_REPORT_TO,
            '[MOPA] Relatorio Diario - ' + district.title() + ' - ' + today.strftime('%Y-%m-%d'),
            html,
            is_html=True,
            cc=config.DAILY_REPORT_CC,
            sender=(config.EMAIL_DEFAULT_NAME, config.EMAIL_DEFAULT_SENDER),
            attachments=[config.REPORTS_DIR + '/' + f_name]
        )

    return "Ok", 200


@tasks.route('/send-daily-survey-replies')
def send_daily_survey_replies():
    """Task to send daily survey answers as PDF"""

    today = date.today()

    response = None

    try:
        response = retry_call(requests.get, fargs=['http://mopa.co.mz:8080/critical-points/' + today.strftime('%Y-%m-%d')], exceptions=ConnectTimeout, tries=3)
    except Exception, ex:
        ex_type, ex_obj, ex_tb = sys.exc_info()
        fname = os.path.split(ex_tb.tb_frame.f_code.co_filename)[1]
        current_app.logger.error("Could not fetch daily survey answers required to generate report.\nError message:{ex_msg}.\nException Type: {ex_type}.\nFile name: {file_name}.\nLine No: {line_no}.\nTraceback: {traceback}".format(ex_msg=str(ex), ex_type=str(ex_type), file_name=str(fname), line_no=str(ex_tb.tb_lineno), traceback=traceback.format_exc()))

    if not response:
        return

    answers = response.json()

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
                if answer.get('answer'):
                    answer["answer"] = 'Nao' if \
                        answer.get('answer') == 'N' else 'Sim'

    # Generate PDF
    if answers:
        del answers[0]  # remove table column labels
    context = {
        'today': today.strftime('%d-%m-%Y'),
        'answers': answers,
        'static': os.path.join(config.BASE_DIR, 'templates') + '/'
    }

    f_name = 'respostas-ao-inquerito-diario-' + today.strftime('%Y_%m_%d') + '.pdf'
    generate_pdf('daily_survey_answers.html', context, f_name)

    # Send mail
    html = '''\
        <html>
            <head></head>
            <body>
            <p>Sauda&ccedil;&otilde;es!<br/><br/>
                Seguem em anexo as respostas aos inqu&eacute;ritos \
                di&aacute;rios<br/><br/>
                Cumprimentos,<br/>
                <em>Enviado automaticamente</em>
            </p>
            </body>
        </html>
            '''
    send_mail(
        config.DAILY_ENQUIRY_REPORT_TO,
        '[MOPA] Respostas aos Inqueritos Diarios - ' + today.strftime('%Y-%m-%d'),
        html,
        is_html=True,
        cc=config.DAILY_REPORT_CC,
        sender=(config.EMAIL_DEFAULT_NAME, config.EMAIL_DEFAULT_SENDER),
        attachments=[config.REPORTS_DIR + '/' + f_name]
    )

    return "Ok", 200


@tasks.route('/send-daily-survey')
def send_daily_survey():
    """Task to send daily survey"""
    survey = Survey(survey_type="G", question=config.SMS_INTRO)
    Uow.add(survey)
    Uow.commit()

    monitor_phones = Location.i().get_monitors_phones()
    for phone in monitor_phones:
        db_sms = SMS.static_send(phone, config.SMS_INTRO)
        Uow.add(db_sms)
        Uow.commit()

    return "Ok", 200


@tasks.route('/check-if-answers-were-received')
def check_if_answers_were_received():
    """Task to check if monitor answered daily survey and alert them if they did not"""
    monitor_phones = Location.i().get_monitors_phones()

    survey = Survey.todays()

    if survey:
        monitors_who_answered = Survey.get_answerers(survey.id) or []

        for phone in monitor_phones:
            if ("258" + phone) not in monitors_who_answered:
                db_sms = SMS.static_send(phone, config.SMS_NO_FEEDBACK_RECEIVED)
                Uow.add(db_sms)
                Uow.commit()

    return "Ok", 200


@tasks.route('/notify-updates-on-requests')
def notify_updates_on_requests():
    """A scheduled task to check if there are any new requests or updated
    requests within the last hour and notify the involved parts"""

    date_format = '%Y-%m-%d'
    today = date.today()
    start_date = today.strftime(date_format)
    end_date = (today + timedelta(days=1)).strftime(date_format)
    recent_requests = get_requests(start_date, end_date, True)

    time_ago = datetime.now(config.TZ) + timedelta(seconds=-(60 * 5))
    now = datetime.now(config.TZ)

    for _request in recent_requests:
        requested_datetime = parse(_request['requested_datetime'])
        updated_datetime = parse(_request['updated_datetime'])
        service_notice = _request['service_notice']
        request_id = _request['service_request_id']

        if (time_ago <= requested_datetime <= now) and service_notice == 'Registado':
            # New request -> notify responsible company/people

            http_response = retry_call(
                requests.get,
                fargs=[config.OPEN311_END_POINTS['people'] + '/' + request_id + '.' + config.OPEN311_RESPONSE_FORMATS['json']],
                exceptions=ConnectTimeout,
                tries=3
            )

            if http_response.status_code != 200:
                current_app.logger.error("Could not find people to notify of new request: %s " % _request['service_request_id'])
                continue

            people = http_response.json()
            phones = map(lambda x: x['phone'], people)

            text = ('MOPA - Novo problema No: %s - %s, %s' % (
                _request['service_request_id'],
                _request['service_name'],
                _request.get('description', '')
            )) \
                .replace('Criado por USSD.', '') \
                .replace('Criado por App.', '')

            for phone in phones:
                SMS.static_send(phone, text)

        elif (time_ago <= updated_datetime <= now) and _request.get('phone', ''):
            # Update on request -> notify the person who reported
            text_tpl = 'Caro municipe, o problema %s tem agora o estado %s. %s'

            if service_notice != 'Em processo':
                text_tpl += '. Caso discorde responda N a esta SMS'

            text = text_tpl % (
                _request['service_request_id'],
                _request['service_notice'],
                _request.get('status_notes', '')
            )

            SMS.static_send(_request.get('phone'), text)

    return "notify-updates-on-requests completed\n", 200


def translate_column_names(df):
    df.rename(columns={'service_notice' : 'Estado', 'district' : 'Distrito', 'service_name' : 'Categoria', 'requested_month' : 'Mes'}, inplace = True)
    return df
