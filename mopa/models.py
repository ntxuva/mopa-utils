# -*- coding: utf-8 -*-
"""
    mopa.models
    -----------

    Contains classes with direct access to the Database
"""
from datetime import *
import os
import sys
import traceback
import requests
from requests.exceptions import ConnectTimeout
import json
from sqlalchemy import *
from sqlalchemy.ext.declarative import DeclarativeMeta
from retry.api import retry_call
import re
from flask import current_app
# Import the database object (db) from the main application module
# this is defined inside __init__.py
# For datetime comparisons w/ SQLAlchemy check
# https://gist.github.com/Tukki/3953990
from mopa import db
from mopa.infrastructure import Location, remove_accents, ustr

DB_PREFIX = os.getenv('DB_PREFIX', 'mopa_')
SC_SMS_END_POINT = os.getenv('SC_SMS_END_POINT')
UX_SMS_END_POINT = os.getenv('UX_SMS_END_POINT')
API_KEY = os.getenv('API_KEY', 'local')

def setup_models():
    """Sets up our DB Models by Dropping and creating the tables again.
    """
    db.drop_all()
    db.create_all()


class Uow():
    """Unit of work like class. Here we use it as a wrapper around db,
    so we don't leak db into other app layers. The idea is to keep all db
    things in the models layer. Should any component require something from the
    db it should ask to the models layer
    """
    @staticmethod
    def add(m):
        db.session.add(m)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
        db.session.flush()  # for resetting non-committed .add()


class BaseModel(db.Model):
    """A base model for other database tables to inherit"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class SMS(BaseModel):
    __tablename__ = DB_PREFIX + "sms"

    direction = db.Column(db.String(1))  # I/O
    sent_by = db.Column(db.String(255))
    sent_to = db.Column(db.String(255))
    text = db.Column(db.String(255))

    def __init__(self, direction, text, sent_by=None, sent_to=None):
        """Constructor"""
        self.direction = direction

        if sent_by is None:
            sent_by = "Mopa"
        self.sent_by = sent_by

        if sent_to is None:
            sent_to = "Mopa"
        self.sent_to = sent_to

        self.text = text

    def __repr__(self):
        """String representation"""
        return '<SMS %r %r %r %r %r>' % (self.direction, self.text, self.sent_by, self.sent_to, self.created_at)

    def send(self):
        """
        Issues an HTTP request to Source Code Solutions end point
        which in turn will forward to destination number
        PS. This must use GET; the `from` param must be in small caps
        """
        # probably save before sending
        if self.direction == 'O' and self.sent_to == 'Mopa':
            raise Exception("Invalid addressee for outgoing message" + str(self))

        to_ux_re = re.compile('^(\+258)8[6|7|4]\d{7}$', re.IGNORECASE)
        is_to_ux = to_ux_re.match(self.sent_to)

        payload = {}
        if is_to_ux:
            payload = {"to[]": self.sent_to, "message": self.text, "API_KEY": API_KEY}
        else:
            payload = {"from": "mopa", "to": self.sent_to, "text": self.text}

        response = None

        # Retry sending request 3 times if safe-retry ConnectTimeout exception is thrown and trap & report other errors
        try:
            if is_to_ux:
                response = retry.call(requests.post, fargs=[UX_SMS_END_POINT], fkwargs={"data": payload}, exceptions=ConnectTimeout, tries=3)
            else:
                response = retry_call(requests.get, fargs=[SC_SMS_END_POINT], fkwargs={"params": payload}, exceptions=ConnectTimeout, tries=3)
            print response
        except Exception, ex:
            ex_type, ex_obj, ex_tb = sys.exc_info()
            fname = os.path.split(ex_tb.tb_frame.f_code.co_filename)[1]
            current_app.logger.error("Error delivering SMS to SMSC.\nError message:{ex_msg}.\nException Type: {ex_type}.\nFile name: {file_name}.\nLine No: {line_no}.\nTraceback: {traceback}".format(ex_msg=str(ex), ex_type=str(ex_type), file_name=str(fname), line_no=str(ex_tb.tb_lineno), traceback=traceback.format_exc()))
            return

        if response and response.status_code == 200: # and response.text.strip() == "Message successfully forwarded from MOPA to SMSC"
            current_app.logger.info("SMS {0} delivered Successfully".format(self.__repr__()))
        else:
            current_app.logger.error("Error while delivering SMS {0}. Status code: {1}, response text: {2}".format(self.__repr__(), str(response.status_code), response.text))

    @staticmethod
    def static_send(to, text):
        """Build new SMS object and send"""
        sms = SMS(direction="O", text=text, sent_by="mopa", sent_to=to)
        sms.send()
        return sms


class Survey(BaseModel):
    """Represents a survey in the Mopa ecosystem."""
    __tablename__ = DB_PREFIX + "survey"

    survey_id = db.Column(db.String(255))
    survey_type = db.Column(db.String(1))  # S(ingle)/G(roup)

    district = db.Column(db.String(255))
    neighbourhood = db.Column(db.String(255))
    point = db.Column(db.String(255))

    question = db.Column(db.String(255))

    def __init__(self, survey_type="I", district=None, neighbourhood=None, point=None, question=None):
        """Constructor"""
        self.survey_id = self.get_next_survey_id()
        self.survey_type = survey_type
        self.question = question

        if survey_type == "I":
            self.district = district
            self.neighbourhood = neighbourhood
            self.point = point

    def __repr__(self):
        """String representation """
        return "<Survey> " + self.survey_id

    def get_next_survey_id(self):
        """The survey id is daily auto-incremental, meaning that each day it will reset to 1 and keep counting till next reset."""
        last_survey = self.get_last_survey()
        today = date.today()
        if not last_survey or (last_survey.created_at.date() < today):
            return 1
        else:
            return int(last_survey.survey_id) + 1

    def get_last_survey(self):
        return self.query.order_by(desc(Survey.id)).first()

    @staticmethod
    def todays():
        """Gets the today's survey"""

        sql = "SELECT id FROM mopa_survey WHERE survey_type='G' AND DATE(created_at) = DATE(NOW()) LIMIT 1;"
        results = db.engine.execute(sql)
        survey_id = None
        for row in results:
            survey_id = row[0]
        survey = Survey.query.filter_by(id=str(survey_id)).first()
        return survey

    @staticmethod
    def get_by_id(id):
        """Get the survey survey_id as given. Note that this is the day ID"""

        sql = "SELECT id FROM mopa_survey WHERE survey_id = %s AND DATE(created_at)  = DATE(NOW()) LIMIT 1;"
        results = db.engine.execute(sql % (id))
        survey_id = None
        for row in results:
            survey_id = row[0]
        survey = Survey.query.filter_by(id=str(survey_id)).first()
        return survey

    def get_by_key(key):
        """Gets the survey with id as given. Note difference w/ get_by_id"""
        survey = Survey.query.filter_by(id=str(key)).first()
        return survey

    @staticmethod
    def get_stats():
        """Get the stats representation of the surveys"""

        sql = """
SELECT
    CONCAT(a.neighbourhood, ' - ', a.point) as area,
    question as message,
    CONCAT(SUM(CASE WHEN LOWER(answer) IN ('yes', 'y', 'sim', 's')
                THEN 1
            ELSE 0
        END),'') as count_yes,
    CONCAT(SUM(CASE WHEN LOWER(answer) IN ('no', 'n', 'nao')
            THEN 1
            ELSE 0
        END),'') as count_no,
    LEFT(CONCAT(a.created_at,''),10) as date
FROM mopa_survey a LEFT JOIN mopa_survey_answers b ON a.id = b.survey_key
WHERE a.survey_type = 'I'
GROUP BY a.question, a.neighbourhood, a.point;
                """
        keys = ["area", "message", "count_yes", "count_no", "date"]
        results = db.engine.execute(sql)
        rows = []
        for row in results:
            rows.append(dict(zip(keys, row)))
        return rows

    @staticmethod
    def get_answerers(key):
        """Gets the phonenumbers of monitors who answered the given survey"""

        sql = "SELECT answered_by FROM mopa_survey_answers WHERE survey_key = %s" % (key)
        rows = []
        results = db.engine.execute(sql)
        for row in results:
            rows.append(row[0])
        return rows

    @staticmethod
    def get_todays_answers():
        """Gets today's answers"""
        sql = """
SELECT a.*
FROM mopa_survey_answers a JOIN mopa_survey b
WHERE b.survey_type = 'G'
    AND a.survey_key = b.id
    AND DATE(a.answered_at) = DATE(NOW());
              """
        keys = ["id", "created_at", "updated_at", "survey_key", "survey_id",
                "answer", "answered_at", "answered_by", "answer_sms_id",
                "neighbourhood", "quarter", "point"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))
        return rows

    @staticmethod
    def get_day_answers(_date):
        """
        Gets the answers for a specific day
        """

        sql = """
SELECT c.sent_to, z.*
FROM mopa_sms c
    LEFT JOIN
        (SELECT a.created_at, UPPER(LEFT(a.answer, 1)) as answer, a.answered_by
         FROM mopa_survey_answers a
            INNER JOIN mopa_survey b
                ON a.survey_key = b.id
                   AND b.survey_type = 'G'
                   AND DATE(a.answered_at) = DATE('{0:s}')
        ) z
        ON CONCAT('258', TRIM(c.sent_to)) = TRIM(z.answered_by)
WHERE c.direction='O'
    AND LEFT(c.`text`, 6) = 'MOPA -'
    AND DATE(c.created_at) = DATE('{0:s}')
        """.format(_date)

        keys = ["sent_to", "created_at", "answer", "answered_by"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))
        return rows

    @staticmethod
    def get_all():
        """
        Gets all surveys
        """
        sql = """
SELECT DISTINCT a.sent_to, d.answered_by, a.created_at, d.answer
FROM mopa_sms a
  LEFT JOIN (SELECT c.created_at,
                    UPPER(LEFT(b.answer, 1)) as answer,
                    b.answered_by
            FROM mopa_survey_answers b
              INNER JOIN mopa_survey c ON b.survey_key=c.id
            WHERE c.survey_type='G') d
    ON CONCAT('258', TRIM(a.sent_to)) = TRIM(d.answered_by) AND
       DATE(a.created_at) = DATE(d.created_at)
WHERE a.direction='O' AND LEFT(a.`text`, 6) = 'MOPA -'
ORDER BY a.created_at, a.sent_to
        """

        keys = ["sent_to", "created_at", "answer", "answered_by"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))

        return rows


class SurveyAnswer(BaseModel):
    """Represents a survey which is sent to every monitor in Mopa
    automatically"""

    __tablename__ = DB_PREFIX + "survey_answers"

    # actual unique identifier for the survey
    survey_key = db.Column(db.Integer, ForeignKey(Survey.id))
    survey_id = db.Column(db.String(255))
    survey = db.relationship("Survey", foreign_keys="SurveyAnswer.survey_key", backref=db.backref("answers", lazy="dynamic"))

    answer = db.Column(db.String(255))
    answered_at = db.Column(db.DateTime)
    answered_by = db.Column(db.String(255))
    answer_sms_id = db.Column(db.Integer, ForeignKey(SMS.id), primary_key=False)
    answer_sms = db.relationship("SMS",  foreign_keys="SurveyAnswer.answer_sms_id", backref=db.backref("answer_smsz",lazy="dynamic"))

    neighbourhood = db.Column(db.String(255))
    quarter = db.Column(db.String(255))
    point = db.Column(db.String(255))

    NEIGHBOURHOODS = []

    def __init__(self, survey_id, answer, answered_by, answer_sms_id=None, survey_key=None):
        """Constructor. TO-DO: The logic to know from which neighbourhood
        is the monitor is faulty as sometimes a monitor is responsible for 2
        points. Meaning that the logic here will get the first or last
        neighbourhood, completely ignoring the rest of the points"""
        self.survey_id = survey_id
        self.answer = answer
        self.answered_by = answered_by
        self.answered_at = datetime.utcnow()
        self.survey_key = survey_key

        if not self.NEIGHBOURHOODS:
            self.NEIGHBOURHOODS = Location.i().get_locations_tree()

        for district in self.NEIGHBOURHOODS["districts"]:
            for neighbourhood in district['neighbourhoods']:
                for point in neighbourhood['points']:
                    for monitor_id in point['monitors']:
                        monitor = Location.i().get_monitor(monitor_id)
                        if (monitor['phone'] == answered_by or
                                "258" + monitor['phone'] == answered_by):
                            self.neighbourhood = neighbourhood['name']
                            self.quarter = ""
                            self.point = (point['name'] +
                                          " " +
                                          point['location'])
                            break

        if answer_sms_id:
            self.answer_sms_id = answer_sms_id

    def __repr__(self):
        pass

    @staticmethod
    def get_survey_answers(survey_id):
        pass


class Report(db.Model):
    """Represents a issue that has been reported.

        Used for reporting purposes only, not operation.
    """
    __tablename__ = DB_PREFIX + "reports"

    # _id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(255), unique=True, primary_key=True)
    district = db.Column(db.String)
    neighbourhood = db.Column(db.String)
    location_name = db.Column(db.String)
    nature = db.Column(db.String)
    requested_datetime = db.Column(db.DateTime)
    updated_datetime = db.Column(db.DateTime)
    type = db.Column(db.String)
    status = db.Column(db.String)
    status_notes = db.Column(db.String)

    def __init__(self):
        pass

    @staticmethod
    def get_summary_report(start_date, end_date, old_start_date, old_end_date):
        """Gets the report summary report Aka Louis' report 1"""
        sql = """
SELECT recent.*, recent.tempo_medio_resolucao - old.tempo_medio_resolucao as variacao
FROM
(
SELECT type,
    COUNT(*) as no_occorencias,
    ROUND((COUNT(*)/b.total_reports * 100),2) as `pct_do_total`,
    AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '{0}' AND '{1}') b
WHERE requested_datetime BETWEEN '{0}' AND '{1}'
GROUP BY type
) AS recent LEFT JOIN
(
SELECT type,
  AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
    ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '{2}' AND '{3}') b
WHERE requested_datetime BETWEEN '{2}' AND '{3}'
GROUP BY type
) AS old
ON recent.type=old.type
        """.format(start_date, end_date, old_start_date, old_end_date)

        keys = ["type", "no_occorencias", "pct_do_total", "tempo_medio_resolucao", "variacao"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))

        return rows

    @staticmethod
    def get_summary_by_district_report(start_date, end_date, old_start_date, old_end_date):
        """Gets the report summary broken down by district according to the provided mode: Weekly or Monthly Aka Louis' report 2"""
        sql = """
SELECT recent.*, recent.tempo_medio_resolucao - old.tempo_medio_resolucao as variacao_do_tempo_medio
FROM
(
SELECT
    district,
    neighbourhood,
    COUNT(*) as no_occorencias,
    ROUND((COUNT(*)/b.total_reports * 100),2) as `pct_do_total`,
    AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
      ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '{0}' AND '{1}') b
WHERE requested_datetime BETWEEN '{0}' AND '{1}'
GROUP BY district, neighbourhood
) AS recent LEFT JOIN
(
SELECT
    district,
    neighbourhood,
    COUNT(*) as no_occorencias,
    ROUND((COUNT(*)/b.total_reports * 100),2) as `pct_do_total`,
    AVG(a.time_diff) `tempo_medio_resolucao`
FROM mopa_reports
  JOIN (SELECT id, TIMESTAMPDIFF(HOUR, requested_datetime, updated_datetime) time_diff FROM mopa_reports) AS a
      ON mopa_reports.id=a.id
  JOIN (SELECT COUNT(*) as total_reports FROM mopa_reports WHERE requested_datetime BETWEEN '{2}' AND '{3}') b
WHERE requested_datetime BETWEEN '{2}' AND '{3}'
GROUP BY district, neighbourhood
) as old
ON recent.district=old.district AND recent.neighbourhood=old.neighbourhood
        """.format(start_date, end_date, old_start_date, old_end_date)
        keys = ["district", "neighbourhood", "no_occorencias", "pct_do_total", "tempo_medio_resolucao", "variacao_do_tempo_medio"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))

        return rows

    @staticmethod
    def get_by_problem(start_date, end_date):
        """Gets the report summary broken down by district according to the
        provided mode: Weekly or Monthly
        Aka Tiago's report
        """
        sql = """
SELECT
  neighbourhood as bairro,
  nature as problema,
  SUM(CASE WHEN status='Registado' THEN 1 ELSE 0 END) AS registado,
  SUM(CASE WHEN status='Em processo' THEN 1 ELSE 0 END) AS em_processo,
  SUM(CASE WHEN status='Resolvido' THEN 1 ELSE 0 END) AS resolvido,
  SUM(CASE WHEN status='Arquivado' THEN 1 ELSE 0 END) AS arquivado,
  SUM(CASE WHEN status='Inválido' THEN 1 ELSE 0 END) AS invalido,
  COUNT(*) total
FROM mopa_reports
WHERE requested_datetime BETWEEN '{0}' AND '{1}'
GROUP BY neighbourhood, nature;
""".format(start_date, end_date)
        keys = ["bairro", "problema", "registado", "em_processo", "resolvido", "arquivado", "invalido", "total"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))

        return rows

    @staticmethod
    def get_worst_critical_points(neighbourhood, start_date, end_date):
        """Get the worst critical points for a certain neighbourhood.
        The worst point will be the one with more reports during the period.
        """
        neighbourhood = ustr(neighbourhood)
        sql = u"""
SELECT a.*, @curRank := @curRank + 1 AS rank
FROM
(
SELECT location_name, COUNT(*) as count
FROM mopa_reports
WHERE neighbourhood='{0}'
    AND requested_datetime BETWEEN '{1}' AND '{2}'
GROUP BY district, neighbourhood, location_name
ORDER BY 2 DESC
LIMIT 5) a, (SELECT @curRank := 0) r
""".format(neighbourhood, start_date, end_date)
        keys = ["location_name", "count", "rank"]
        query_result = db.engine.execute(sql)
        rows = []
        for row in query_result:
            rows.append(dict(zip(keys, row)))

        return rows
