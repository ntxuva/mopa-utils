# -*- coding: utf-8 -*-
"""
    mopa.tasks
    ----------

    Contains the scheduled tasks definition
"""
import os
import sys

from datetime import datetime, date, timedelta
from dateutil.parser import parse
import requests
from requests.exceptions import ConnectTimeout

from retry.api import retry_call
import traceback
from flask import Blueprint, current_app, request, abort

import mopa.config as config
from mopa.infrastructure import Location, xstr, snake_case, remove_accents, get_requests, generate_pdf, send_mail, truncate
from mopa.models import Uow, SMS, Survey, Report


bp = tasks = Blueprint('tasks', __name__)


@tasks.before_request
def before_request():
    """Checks if API_KEY is valid"""
    api_key = request.headers.get('API_KEY', None)
    if not api_key or api_key != current_app.config['API_KEY']:
        abort(403)  # Forbidden / Not Authorized


@tasks.route('/send-weekly-report')
def send_weekly_report():
    """Task to run weekly for report"""

    today = date.today()
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
        u"Lixeira informal",
        u"Lixo fora do contentor",
        u"Lixo na vala de drenagem",
        u"Camião não passou",
        u"Contentor a Arder"
    ]

    problem_images = map(lambda x: snake_case(remove_accents(x)), problem_types)

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
        '[MOPA] - Relatorio Semanal - ' + today.strftime('%Y-%m-%d'),
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
    return "Ok", 200


@tasks.route('/send-daily-report')
def send_daily_report():
    """Task to run the Daily PDF Exporter"""

    TODAY = date.today()
    LOCATIONS = Location.i().get_locations_offline()

    # Get requests
    default = ''
    requests_list = []

    start_date = (TODAY + timedelta(days=-2)).strftime('%Y-%m-%d')
    end_date = TODAY.strftime('%Y-%m-%d')

    for _request in get_requests(start_date, end_date, None):

        location = Location.i().guess_location(_request)

        district = location['district']
        neighbourhood = location['neighbourhood']
        location_name = location['location_name']

        requests_list.append({
                'id': xstr(_request['service_request_id']),
                'district': district,
                'neighbourhood': neighbourhood,
                'location_name': location_name,
                'nature': xstr(_request['service_name']),
                'datetime': (xstr(_request['requested_datetime'])[0:10] +
                             " " +
                             xstr(_request['requested_datetime'])[11:19]),
                'type': xstr(_request['service_name']),
                'status': xstr(_request['service_notice']),
                'status_notes': xstr(_request.get('status_notes', ''))
            })

    # sorting
    requests_list = sorted(requests_list,
                           key=lambda i: (i['district'],
                                          i['neighbourhood'],
                                          i['nature'],
                                          i['datetime']))

    # Generate PDF
    context = {
        'today': TODAY.strftime('%d-%m-%Y'),
        'requests_list': requests_list,
        'static': os.path.join(config.BASE_DIR, 'templates') + '/'
    }

    f_name = 'relatorio-diario-' + TODAY.strftime('%Y_%m_%d') + '.pdf'
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
        '[MOPA] - Relatorio Diario - ' + TODAY.strftime('%Y-%m-%d'),
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
        response = retry_call(requests.get, fargs=['http://mopa.co.mz:5000/critical-points/' + today.strftime('%Y-%m-%d')], exceptions=ConnectTimeout, tries=3)
    except Exception, ex:
        ex_type, ex_obj, ex_tb = sys.exc_info()
        fname = os.path.split(ex_tb.tb_frame.f_code.co_filename)[1]
        current_app.logger.error("Could not fetch daily survey answers required to generate report.\nError message:{ex_msg}.\nException Type: {ex_type}.\nFile name: {file_name}.\nLine No: {line_no}.\nTraceback: {traceback}").format(ex_msg=str(ex), ex_type=str(ex_type), file_name=str(fname), line_no=str(ex_tb.tb_lineno), traceback=traceback.format_exc())

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
        '[MOPA] - Respostas aos Inqueritos Diarios - ' + today.strftime('%Y-%m-%d'),
        html,
        is_html=True,
        cc=config.DAILY_REPORT_CC,
        sender=(config.EMAIL_DEFAULT_NAME, config.EMAIL_DEFAULT_SENDER),
        attachments = [config.REPORTS_DIR + '/' + f_name]
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

    today = date.today()

    start_date = (today).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    requests = get_requests(start_date, end_date, True)

    hour_ago = datetime.now(config.TZ) + timedelta(seconds=-(60 * 10))
    now = datetime.now(config.TZ)
    for _request in requests:
        requested_datetime = parse(_request['requested_datetime'])
        updated_datetime = parse(_request['updated_datetime'])
        status = _request['status']

        if hour_ago <= requested_datetime <= now and status == 'open':
            # New request -> notify responsible company/people
            location = Location.i().guess_location(_request)
            district = location['district']
            location_name = location['location_name']

            neighbourhood = location['neighbourhood']
            if neighbourhood:
                phones = Location.i().get_notified_companies_phones(_request['neighbourhood'], _request['service_code'])

                for phone in phones:
                    text_tpl = 'Novo problema reportado no mopa: No: %s - %s em %s. %s'
                    text = text_tpl % (_request['service_request_id'], _request['service_name'], _request['neighbourhood'], _request.get('description', '').replace('Criado por USSD.', ''))
                    text = truncate(text, 160)
                    db_sms = SMS.static_send(phone,text)
                    Uow.add(db_sms)
                Uow.commit()
            else:
                current_app.logger.error("New request with no neighbourhood data found. Cannot notify companies. Request ID: " + _request['service_request_id'])

        elif (hour_ago <= updated_datetime <= now) and status != 'open' and _request.get('phone', ''):
            # Update on request -> notify the person who reported
            text_tpl = 'Caro cidadao, o problema reportado por si: %s foi actualizado. Novo estado: %s. Comentario CMM:'
            text = text_tpl % (_request['service_request_id'], _request['service_notice'],  _request.get('status_notes', ''))
            text = truncate(text, 160)
            db_sms = SMS.static_send(_request.get('phone'), text)
            Uow.add(db_sms)
            Uow.commit()

    return "Ok", 200
