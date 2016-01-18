# -*- coding: utf-8 -*-
"""
    mopa.tasks
    ----------

    Contains the scheduled tasks definition
"""
import os
import sys
import schedule
import json
import time
from datetime import datetime, date, timedelta
from dateutil.parser import parse
import requests
import traceback

from mopa import app
import mopa.constants as constants
import mopa.common as common
from mopa.common import Location, MyJSONEncoder, xstr, ustr
from mopa.models import Uow, SMS, Survey, SurveyAnswer, Report


def send_weekly_report():
    """Task to run weekly for report"""
    app.logger.info("--- Extracting and Sending Weekly Report ---")
    try:
        TODAY = date.today()
        start_date = TODAY + timedelta(days=-7)  # -7
        end_date = TODAY

        old_start_date = start_date + timedelta(days=-7)  # -7
        old_end_date = start_date

        # Get requests
        default = ''
        requests_list = []

        for request in common.get_requests(start_date, end_date, True):
            location = Location.i().guess_location(request)

            del request['zipcode']
            del request['lat']
            del request['long']

            district = location['district']
            neighbourhood = location['neighbourhood']
            location_name = location['location_name']

            report = Report()
            report.id = xstr(request['service_request_id'])
            report.district = district
            report.neighbourhood = neighbourhood
            report.location_name = location_name
            report.nature = xstr(request['service_name'])
            report.requested_datetime = (
                xstr(request['requested_datetime'])[0:10] +
                " " +
                xstr(request['requested_datetime'])[11:19])
            report.updated_datetime = (
                xstr(request['updated_datetime'])[0:10] +
                " " +
                xstr(request['updated_datetime'])[11:19])
            report.type = xstr(request['service_name'])
            report.status = xstr(request['service_notice'])
            report.status_notes = xstr(request.get('status_notes', ''))

            Uow.add(report)
            try:
                Uow.commit()
            except Exception, ex:
                Uow.rollback()
                app.logger.error("Error While Inserting Report in DB\n" +
                                 traceback.format_exc())

        # Report by State
        # ---------------
        estados_report_rows = Report.get_summary_report(start_date,
                                                        end_date,
                                                        old_start_date,
                                                        old_end_date)
        # calculate totals for states
        total_occurencies = 0
        total_pct = 0
        total_tempo_medio_resolucao = 0
        total_variacao = 0

        for estado in estados_report_rows:
            total_occurencies += estado["no_occorencias"]
            total_pct += estado["pct_do_total"]
            total_tempo_medio_resolucao += estado["tempo_medio_resolucao"]
            total_variacao += \
                estado.get("variacao") if estado.get("variacao") else 0

        estados_report_rows.append({
            'type': 'TOTAL',
            'no_occorencias': total_occurencies,
            'pct_do_total': total_pct,
            'tempo_medio_resolucao': total_tempo_medio_resolucao,
            'variacao': total_variacao
        })

        # Report by District
        # ------------------
        district_rows = Report.get_summary_by_district_report(start_date,
                                                              end_date,
                                                              old_start_date,
                                                              old_end_date)
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

            district_totals[row["district"]]["no_occorencias"] += \
                row["no_occorencias"]
            district_totals[row["district"]]["pct_do_total"] += \
                row["pct_do_total"]
            district_totals[row["district"]]["tempo_medio_resolucao"] += \
                row["tempo_medio_resolucao"]
            district_totals[row["district"]]["variacao"] += \
                row.get("variacao", 0)

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

        problem_images = [
            "tchova_nao_passou",
            "contentor_esta_cheio",
            "lixeira_informal",
            "lixo_fora_do_contentor",
            "lixo_na_vala_de_drenagem",
            "camiao_nao_passou",
            "contentor_a_arder"
        ]

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
                t_neighbourhoods[neighbourhood]["most_frequent_problem"] = \
                    t_neighbourhoods[neighbourhood]["rows"][0]["problema"]
            else:
                t_neighbourhoods[neighbourhood]["most_frequent_problem"] = None

            t_neighbourhoods[neighbourhood]["rows"] = sorted(
                t_neighbourhoods[neighbourhood]["rows"],
                key=lambda i: (-1 * i['resolvido'])
            )

            if t_neighbourhoods[neighbourhood]["rows"][0]["resolvido"] > 0:
                t_neighbourhoods[neighbourhood]["most_solved_problem"] = \
                    t_neighbourhoods[neighbourhood]["rows"][0]["problema"]
            else:
                t_neighbourhoods[neighbourhood]["most_solved_problem"] = None

            t_neighbourhoods[neighbourhood]["rows"] = sorted(
                t_neighbourhoods[neighbourhood]["rows"],
                key=lambda i: (-1 * i['total'])
            )

        for neighbourhood in t_neighbourhood_names:
            t_neighbourhoods[neighbourhood]["worst_critical_points"] = \
                Report.get_worst_critical_points(neighbourhood,
                                                 start_date,
                                                 end_date)

        # Generate PDF
        context = {
            'today': TODAY.strftime('%d-%m-%Y'),
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
            'static': os.path.join(constants.BASE_DIR, 'templates') + '/'
        }
        f_name = 'relatorio-semanal-' + TODAY.strftime('%Y_%m_%d') + '.pdf'
        common.generate_pdf('weekly_report.html', context, f_name)

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
        common.mail(
            constants.WEEKLY_REPORT_TO,
            constants.DAILY_REPORT_CC,
            'MOPA - Relatorio Semanal - ' + TODAY.strftime('%Y-%m-%d'),
            html,
            constants.REPORTS_DIR + '/' + f_name)
    except Exception, ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app.logger.error("--- Error running Weekly Report ---" + "\n" +
                         str(ex) + ' ' +
                         str(exc_type) + ' ' +
                         str(fname) + ' ' +
                         str(exc_tb.tb_lineno) + "\n" +
                         traceback.format_exc())
    else:
        app.logger.info("--- Succesfully run Weekly Report ---")


def send_mothly_report():
    """Task to prepare and send the monthly report"""
    pass


def send_daily_report():
    """Task to run the Daily PDF Exporter"""
    app.logger.info("--- Extracting and Sending Daily Report ---")
    try:
        TODAY = date.today()
        LOCATIONS = Location.i().get_locations_offline()

        # Get requests
        default = ''
        requests_list = []

        start_date = (TODAY + timedelta(days=-2)).strftime('%Y-%m-%d')
        end_date = TODAY.strftime('%Y-%m-%d')

        for request in common.get_requests(start_date, end_date, None):

            location = Location.i().guess_location(request)

            district = location['district']
            neighbourhood = location['neighbourhood']
            location_name = location['location_name']

            requests_list.append({
                    'id': xstr(request['service_request_id']),
                    'district': district,
                    'neighbourhood': neighbourhood,
                    'location_name': location_name,
                    'nature': xstr(request['service_name']),
                    'datetime': (xstr(request['requested_datetime'])[0:10] +
                                 " " +
                                 xstr(request['requested_datetime'])[11:19]),
                    'type': xstr(request['service_name']),
                    'status': xstr(request['service_notice']),
                    'status_notes': xstr(request.get('status_notes', ''))
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
            'static': os.path.join(constants.BASE_DIR, 'templates') + '/'
        }

        f_name = 'relatorio-diario-' + TODAY.strftime('%Y_%m_%d') + '.pdf'
        common.generate_pdf('daily_report.html', context, f_name)

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
        common.mail(
            constants.DAILY_REPORT_TO,
            constants.DAILY_REPORT_CC,
            'MOPA - Relatorio Diario - ' + TODAY.strftime('%Y-%m-%d'),
            html,
            constants.REPORTS_DIR + '/' + f_name)
    except Exception, ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app.logger.error("--- Error running Daily Report ---" + "\n" +
                         str(ex) + ' ' +
                         str(exc_type) + ' ' +
                         str(fname) + ' ' +
                         str(exc_tb.tb_lineno) + "\n" +
                         traceback.format_exc())
    else:
        app.logger.info("--- Succesfully run Daily Report ---")


def send_daily_survey_replies():
    """Task to send daily survey answers as PDF"""
    app.logger.info("- Extracting and Sending Daily Survey Replies Report -")
    try:
        TODAY = date.today()
        response = requests.get('http://mopa.co.mz:5000/critical-points/' +
                                TODAY.strftime('%Y-%m-%d'))

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
        del answers[0]
        context = {
            'today': TODAY.strftime('%d-%m-%Y'),
            'answers': answers,
            'static': os.path.join(constants.BASE_DIR, 'templates') + '/'
        }

        f_name = 'respostas-ao-inquerito-diario-' + \
                 TODAY.strftime('%Y_%m_%d') + \
                 '.pdf'
        common.generate_pdf('daily_survey_answers.html', context, f_name)

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
        common.mail(
            constants.DAILY_ENQUIRY_REPORT_TO,
            constants.DAILY_REPORT_CC,
            'MOPA - Respostas aos Inqueritos Diarios - ' +
            TODAY.strftime('%Y-%m-%d'),
            html,
            constants.REPORTS_DIR + '/' + f_name)
    except Exception, ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app.logger.error("-- Error running Daily Survey Replies Report --\n" +
                         str(ex) + ' ' +
                         str(exc_type) + ' ' +
                         str(fname) + ' ' +
                         str(exc_tb.tb_lineno) + "\n" +
                         traceback.format_exc())
    else:
        app.logger.info("-- Succesfully run Daily Survey Replies Report --")


def send_daily_survey():
    """Task to send daily survey"""
    app.logger.info("--- Sending daily G survey ---")

    try:
        survey = Survey(survey_type="G", question=constants.SMS_INTRO)
        Uow.add(survey)
        Uow.commit()

        monitor_phones = Location.i().get_monitors_phones()
        for phone in monitor_phones:
            db_sms = SMS.static_send(phone, constants.SMS_INTRO)
            Uow.add(db_sms)
            Uow.commit()
    except Exception, ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app.logger.error("--- Error Sending daily G survey ---" + "\n" +
                         str(ex) + ' ' +
                         str(exc_type) + ' ' +
                         str(fname) + ' ' +
                         str(exc_tb.tb_lineno) + "\n" +
                         traceback.format_exc())
    else:
        app.logger.info("--- Succesfully Sent daily G survey ---")


def check_if_answers_were_received():
    """Task to check if monitor answered daily survey and alert them if they
        did not"""
    app.logger.info("--- Checking if monitors answered G survey ---")

    try:
        monitor_phones = Location.i().get_monitors_phones()
        monitors_who_answered = []

        survey = Survey.todays()

        if survey:
            monitors_who_answered = Survey.get_answerers(survey.id)

            for phone in monitor_phones:
                if ("258" + phone) not in monitors_who_answered:
                    db_sms = SMS.static_send(
                                phone,
                                constants.SMS_NO_FEEDBACK_RECEIVED)
                    Uow.add(db_sms)
                    Uow.commit()
    except Exception, ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app.logger.error("Error while Checking if monitors answered G survey" +
                         "\n" +
                         str(ex) + ' ' +
                         str(exc_type) + ' ' +
                         str(fname) + ' ' +
                         str(exc_tb.tb_lineno) + "\n" + traceback.format_exc())
    else:
        app.logger.info("Succesfully Checked if monitors answered G survey")


def notify_updates_on_requests():
    """A scheduled task to check if there are any new requests or updated
    requests within the last hour and notify the involved parts"""
    app.logger.info("--- Notifying of updates on requests ---")

    try:
        TODAY = date.today()

        start_date = (TODAY).strftime('%Y-%m-%d')
        end_date = (TODAY + timedelta(days=1)).strftime('%Y-%m-%d')
        requests = common.get_requests(start_date, end_date, True)

        HOUR_AGO = datetime.now(constants.TZ) + timedelta(seconds=-(60 * 10))
        NOW = datetime.now(constants.TZ)
        for request in requests:
            requested_datetime = parse(request['requested_datetime'])
            updated_datetime = parse(request['updated_datetime'])
            status = request['status']

            if (requested_datetime >= HOUR_AGO and
                    requested_datetime <= NOW and
                    status == 'open'):
                # New request -> notify responsible company/people
                location = Location.i().guess_location(request)
                district = location['district']
                location_name = location['location_name']
                neighbourhood = location['neighbourhood']
                if neighbourhood:
                    phones = Location.i().get_notified_companies_phones(
                            neighbourhood, request['service_code'])
                    for phone in phones:
                        db_sms = SMS.static_send(
                                    phone,
                                    'Novo problema reportado no mopa: \
                                     Numero de Ocorrencia: %s - %s - %s \
                                     em %s - %s - %s' %
                                    (request['service_request_id'],
                                     request['service_name'],
                                     request['description'].
                                        replace('Criado porUSSD. ', ''),
                                     district,
                                     neighbourhood,
                                     location_name)
                                )
                        Uow.add(db_sms)
                    Uow.commit()
                else:
                    app.logger.error("New request with no neighbourhood data \
                                     found. Cannot notify companies. \
                                     Request ID: " +
                                     request['service_request_id'])

            elif(updated_datetime >= HOUR_AGO and
                 updated_datetime <= NOW and
                 status != 'open'):
                # Update on request -> notify the person who reported
                phone = request.get('phone', '')
                if phone:
                    db_sms = SMS.static_send(
                                phone,
                                'Caro cidadao, o problema reportado por si: ' +
                                request['service_request_id'] +
                                ' foi actualizado. Novo estado: ' +
                                request['service_notice'] +
                                '. Comentario CMM: ' +
                                request.get('status_notes', '') +
                                '. Obrigado pelo seu contributo. Mopa'
                            )
                    Uow.add(db_sms)
                    Uow.commit()
    except Exception, ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        app.logger.error("Error while Notifying of updates on requests \n " +
                         str(ex) + ' ' +
                         str(exc_type) + ' ' +
                         str(fname) + ' ' +
                         str(exc_tb.tb_lineno) + "\n" +
                         traceback.format_exc())
    else:
        app.logger.info("--- Succesfully Notified of updates on requests ---")


def setup_tasks():
    """Sets up all scheduled tasks.
    Note: The production server is in portugal so set tasks
    to run one hour behind. What is meant to run at 20 must run at 19
    """
    if not app.debug:
        # Production Schedule
        schedule.every(10).minutes.do(notify_updates_on_requests)
        schedule.every().day.at("17:30").do(send_daily_survey)
        schedule.every().day.at("18:30").do(check_if_answers_were_received)
        schedule.every().day.at("19:00").do(send_daily_report)
        schedule.every().day.at("19:15").do(send_daily_survey_replies)
        schedule.every().sunday.at("19:30").do(send_weekly_report)
    else:
        # Test Schedule
        schedule.every(2).seconds.do(notify_updates_on_requests)
        schedule.every(5).seconds.do(send_daily_survey)
        schedule.every(7).seconds.do(check_if_answers_were_received)
        schedule.every(9).seconds.do(send_daily_report)
        schedule.every(10).seconds.do(send_daily_survey_replies)
        schedule.every(20).seconds.do(send_weekly_report)


def run_scheduler():
    """Runs pending scheduled tasks."""
    while True:
        schedule.run_pending()
        time.sleep(1)
