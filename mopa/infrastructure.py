# -*- coding: utf-8 -*-

import os
import sys

import json
from decimal import Decimal
from datetime import *

import functools
from retry import retry
from retry.api import retry_call

from threading import Thread, Lock

import six

from mopa import config


###############################################################################
# String ######################################################################
###############################################################################
import re
import unicodedata
import string

default = ''

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def xstr(s):
    """empty string helper"""
    return s or ''


def ustr(s):
    """Converts a string to unicode"""
    # return six.text_type(s)
    if not s:
        return u''
    if isinstance(s, unicode):
        return s
    return unicode(s, "utf-8")


def truncate(s, length):
    return s[:length]


def remove_accents(data):
    data = ustr(data)
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters or x == " ")


def snake_case(string):
    s1 = FIRST_CAP_RE.sub(r'\1_\2', string)
    return ALL_CAP_RE.sub(r'\1_\2', s1).lower()

###############################################################################
# HTTP ########################################################################
###############################################################################

from flask.json import JSONEncoder
from decimal import Decimal

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            try:
                return float(o)
            except:
                return super(JSONEncoder, self)._iterencode(o, markers)

        if isinstance(o, (date, datetime)):
            return o.isoformat()

        if isinstance(o, datetime.timedelta):
            return str(o)

        return super(JSONEncoder, self)._iterencode(o)

###############################################################################
# Util ########################################################################
###############################################################################

import time
import traceback
import logging


def trap_errors(name):
    """Wrapps a function within a try-catch-else to trap and report errors"""
    def trap_errors_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            logger.info("--- Running : {0} ---".format(name))
            rv = None
            try:
                rv = func(*args, **kwargs)
            except Exception, ex:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error(
                    "Error running -- " + name +  " in " + func.__name__ + " " + "\n" +
                    str(ex) + ' ' +
                    str(exc_type) + ' ' +
                    str(fname) + ' ' +
                    str(exc_tb.tb_lineno) + "\n" +
                    traceback.format_exc()
                )
            else:
                logger.info("--- Successfully run : {0} ---".format(name))

            if rv:
                return rv
        return wrapper
    return trap_errors_decorator


def asynchronously(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.daemon = True # Daemonize thread to allow stopping with CTRL+C
        thr.start() # Start the execution
        # Calling join() on a thread tells the main thread to wait for this particular thread to finish before the main thread can execute the next instruction.
        return thr
    return wrapper


def is_int(s):
    """Checks if a given string is a number of not."""
    try:
        int(s)
        return True
    except ValueError:
        return False



import pprint as _pprint


def pprint(o):
    """pretty prints a given object to stdout"""
    pp = _pprint.PrettyPrinter(indent=4)
    pp.pprint(o)


def ppformat(o):
    """pretty prints a given object and returns it's string"""
    return _pprint.pformat(o)



from xhtml2pdf import pisa
from jinja2 import Template, Environment, PackageLoader


def generate_pdf(template, context, name):
    """Generates PDF files based on given input

    :param template: the template filename including the extension
    :param context: the context object to be used while rendering the template
    :param name: the name to be given to PDF file in disk including the extension
    """

    # Get jinja2 template
    pisa.showLogging()
    env = Environment(loader=PackageLoader('mopa', 'templates'))
    template = env.get_template(template)
    html = template.render(context)

    # Write PDF to file
    file_name = os.path.join(config.REPORTS_DIR, name)

    with open(file_name + '.html', "w+b") as f_html:
        f_html.write(html.encode('utf-8'))

    with open(file_name, "w+b") as f_pdf:
        pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=f_pdf)

        # Return PDF document for mail sending
        f_pdf.seek(0)
        pdf = f_pdf.read()
        f_pdf.close()
        return pdf

###############################################################################
# Patterns ####################################################################
###############################################################################


class Singleton(object):
    # Based on tornado.ioloop.IOLoop.instance() approach.
    # See https://github.com/facebook/tornado
    __singleton_lock = Lock()
    __singleton_instance = None

    @classmethod
    def i(cls):
        """the common sense method to retrieve the instance"""
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


###############################################################################
# App #     ###################################################################
###############################################################################

import requests
from requests.exceptions import ConnectTimeout


def get_requests(start_date, end_date, include_phone):
    """Gets the problems registered in the refereed time stamp.
    dates must be a string in YYYY-MM-dd format (eg. '2015-08-01')"""
    phone_key = config.OPEN311_PHONE_KEY if include_phone else ''
    payload = {'start_date': start_date, 'end_date': end_date, 'phone_key': phone_key}

    http_response = retry_call(
        requests.get,
        fargs=[config.OPEN311_END_POINTS['requests'] + '.' + config.OPEN311_RESPONSE_FORMATS['json']],
        fkwargs={'params': payload},
        exceptions=ConnectTimeout,
        tries=3
    )

    if http_response.status_code != 200:
        return []

    return http_response.json()


def get_report_file_params(filename):
    filepath = config.REPORTS_DIR + "/" + filename

    if os.path.isfile(filepath):
        return filename, "/reports/" + filename, os.path.getsize(filepath)

    return None


class Location(Singleton):
    """Helper class for all location needs.
    usage: Location.i().method()
    """

    NEIGHBOURHOODS = LOCATIONS = ONLINE_LOCATIONS = None

    def get_locations_offline(self):
        """loads locations.json file and converts into a python list"""
        if self.LOCATIONS:
            return self.LOCATIONS

        data = ""
        with open(name=config.BASE_DIR + '/static/locations.json', mode='r') as f:
            for line in f.readlines():
                data += line
        self.LOCATIONS = json.loads(data)

        return self.LOCATIONS

    def get_locations_online(self):
        """loads the locations from the API and converts into a python list"""
        if self.ONLINE_LOCATIONS:
            return self.ONLINE_LOCATIONS
        r = None
        try:
            r = retry_call(requests.get, fargs=[config.OPEN311_BASE_URL + "locations.json"], exceptions=ConnectTimeout, tries=3)
        except:
            pass

        if r and r.status_code == 200:
            z_json = str(r.text.decode("utf-8").encode("ascii", "ignore")).strip("'<>()\"` ").replace('\'', '\"')
            self.ONLINE_LOCATIONS = json.loads(z_json)
            return self.ONLINE_LOCATIONS
        else:
            return []

    def get_location_offline(self, latitude, longitude):
        """Get data about a known point in mopa context.
        This data comes from the neighbourhoods.json file
        """
        _return = {
            'district':      "",
            'location_name': "",
            'neighbourhood': ""
        }

        for location in self.get_locations_offline():
            if location[u'location_type'] in [u'container', u'quarter', u'critical point']:

                f_latitude  = float(location[u'lat'].strip(u'\u200b'))
                f_longitude = float(location[u'long'].strip(u'\u200b'))

                if float(latitude) == f_latitude and float(longitude) == f_longitude:
                    _return[u'district']        = location[u'district']
                    _return[u'location_name']   = location[u'location_name']
                    _return[u'neighbourhood']   = location[u'neighbourhood'][0] if location.get('neighbourhood') and type(location.get('neighbourhood')) is list else u''

        return _return

    def get_location_online(self, location_id=None, latitude=0, longitude=0):
        """Get the location data based on the online locations.json"""
        _return = {
            'district':      "",
            'location_name': "",
            'neighbourhood': ""
        }

        if not self.ONLINE_LOCATIONS:
            self.ONLINE_LOCATIONS = self.get_locations_online()

        if location_id is not None:
            for location in self.ONLINE_LOCATIONS:
                if location["location_id"] == location_id:
                    _return[u'district']        = location[u'district']
                    _return[u'location_name']   = location[u'location_name']
                    _return[u'neighbourhood']   = location[u'neighbourhood'][0] if location.get('neighbourhood') and type(location.get('neighbourhood')) is list else u''

        elif latitude and longitude:
            lat_len = len(str(latitude).split('.')[1])
            long_len = len(str(longitude).split('.')[1])

            for location in self.ONLINE_LOCATIONS:
                # Sometimes locations come with weird spaces so we remove them
                f_latitude = location["lat"].strip(u'\u200b')
                f_longitude = location["long"].strip(u'\u200b')

                if round(float(f_latitude), lat_len) == latitude and round(float(f_longitude), long_len) == longitude:
                    _return[u'district']        = location[u'district']
                    _return[u'location_name']   = location[u'location_name']
                    _return[u'neighbourhood']   = location[u'neighbourhood'][0] if location.get('neighbourhood') and type(location.get('neighbourhood')) is list else u''

        elif not _return[u'district']:

            latitude = round(float(latitude), 6)
            longitude = round(float(longitude), 6)

            for location in self.ONLINE_LOCATIONS:
                if round(float(location["lat"].strip()), 6) == latitude and round(float(location["long"].strip()), 6) == longitude:
                    _return[u'district']        = location[u'district']
                    _return[u'location_name']   = location[u'location_name']
                    _return[u'neighbourhood']   = location[u'neighbourhood'][0] if location.get('neighbourhood') and type(location.get('neighbourhood')) is list else u''

        return _return

    def guess_location(self, request):
        """Guesses what is the district, location_name and neighbourhood for
        a given report and returns them as a tuple"""

        _return = {
            'district':      "",
            'location_name': "",
            'neighbourhood': ""
        }

        district = ''
        location_name = xstr(request.get('address', default))
        neighbourhood = xstr(request.get('neighbourhood', default))

        # get location online with address_id
        if not district:
            if request.get('address_id', default):
                address_id = request.get('address_id', default)
                location = self.get_location_online(location_id=address_id)
                district = location['district']
                if not district:
                    district = ''
                if not location_name:
                    location_name = location['location_name']
                if not neighbourhood:
                    neighbourhood = location['neighbourhood']

        # No textual location so get it from the description.
        if len(district) == 0 or len(location_name) == 0:
            description = request.get('description', default)
            if description and description.startswith('Criado por USSD'):
                description = description.replace('Criado por USSD. ', '').replace('Criado por App. ', '')
                district = description.partition(', Bairro: ')[0].replace('Distrito: ', '')
                location_name = (description.partition(neighbourhood)[2]).strip(',')
        """
        # No textual location so get it from offline locations
        if len(district) == 0 or len(location_name) == 0:
            location = self.get_location_offline(latitude=request.get('lat', default), longitude=request.get('long', default))

            district = location['district']
            if not district:
                district = '-'
            if not location_name:
                location_name = location['location_name']
            if not neighbourhood:
                neighbourhood = location['neighbourhood']

        # No textual description so finally get from online from latitude and longitude
        if len(district) == 0 or len(location_name) == 0:
            location = self.get_location_online(latitude=request.get('lat', default), longitude=request.get('long', default))

            district = location['district']
            if not district:
                district = '-'
            if not location_name:
                location_name = location['location_name']
            if not neighbourhood:
                neighbourhood = location['neighbourhood']
        """
        _return['district'] = district
        _return['location_name'] = location_name
        _return['neighbourhood'] = neighbourhood
        return _return

    ##################

    def get_notifications_mapping(self):
        """loads neighbourhoods.json file and returns as a python object."""
        if self.NEIGHBOURHOODS:
            return self.NEIGHBOURHOODS

        data = ""
        with open(name=os.path.join(config.BASE_DIR, config.NEIGHBOURHOODS_JSON_PATH), mode="r") as f:
            for line in f.readlines():
                data += line
        self.NEIGHBOURHOODS = json.loads(data)

        return self.NEIGHBOURHOODS

    def get_monitor(self, _id):
        """Gets a specific monitors details"""
        neighbourhoods = self.get_notifications_mapping()
        for monitor in neighbourhoods['monitors']:
            if str(monitor['id']) == str(_id) or int(monitor['id']) == int(_id):
                return monitor
        return None

    def get_monitors_phones(self):
        """Get the list of all monitors phone numbers"""
        monitor_phones = []
        neighbourhoods = self.get_notifications_mapping()
        for monitor in neighbourhoods['monitors']:
            if monitor['phone']:
                monitor_phones.append(monitor['phone'])
        return monitor_phones

    def get_notified_person(self, _id):
        """Gets the details of one to be notified"""
        neighbourhoods = self.get_notifications_mapping()
        for person in neighbourhoods["notified_people"]:
            if str(person["id"]) == str(_id):
                return person
        return None

    def get_monitor_by_phone(self, phone):
        """Gets the details of a monitor using his phone number"""
        neighbourhoods = self.get_notifications_mapping()
        for monitor in neighbourhoods["monitors"]:
            if str(monitor["phone"]) == str(phone):
                return monitor
        return None

    def get_monitor_point(self, monitor_id):
        """Gets the point data a given monitor"""
        point_data = {}
        neighbourhoods = self.get_notifications_mapping()
        for district in neighbourhoods["districts"]:
            for neighbourhood in district["neighbourhoods"]:
                for point in neighbourhood["points"]:
                    if monitor_id in point["monitors"] or str(monitor_id) in point["monitors"]:
                        point_data["name"] = point["name"]
                        point_data["location"] = point["location"]
                        point_data["geo_location"] = point["geo_location"]
                        point_data["neighbourhood"] = neighbourhood["name"]
                        point_data["district"] = district["name"]
                        return point_data
        return point_data

    def get_notified_companies_phones(self, neighbourhood, service_code):
        """Gets the list of phone numbers which must be notified for problems
        with the given service_code in the given neighbourhood"""
        notified_phones = []
        neighbourhoods = self.get_notifications_mapping()
        for district in neighbourhoods['districts']:
            for _neighbourhood in district['neighbourhoods']:
                if _neighbourhood['name'] == neighbourhood:
                    for notified_people_group in _neighbourhood['notified_people_by_problem']:
                        if notified_people_group['service_code'] == service_code:
                            for _id in notified_people_group['people']:
                                person = self.get_notified_person(_id)
                                if person:
                                    notified_phones.append(person['phone'])
        return notified_phones
