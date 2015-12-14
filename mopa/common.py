# -*- coding: utf-8 -*-
"""
    mopa.common
    -----------

    Contains system wide common utilities for mopa
"""
# import simplejson as json
import json
import os
from decimal import Decimal
from datetime import *
import requests
import constants
import pprint as _pprint
import singleton

import smtplib
import functools
from xhtml2pdf import pisa
from jinja2 import Template, Environment, PackageLoader
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

from mopa import app
default = ''


def xstr(s):
    """empty string helper"""
    return s or ''


def ustr(s):
    """Converts a string to unicode"""
    if not s:
        return u''
    return unicode(s, "utf-8")


def is_int(s):
    """Checks if a given string is a number of not."""
    try:
        int(s)
        return True
    except ValueError:
        return False


def pprint(o):
    """pretty prints a given object to stdout"""
    pp = _pprint.PrettyPrinter(indent=4)
    pp.pprint(o)


def ppformat(o):
    """pretty prints a given object and returns it's string"""
    return _pprint.pformat(o)


def get_requests(start_date, end_date, include_phone):
    """Gets the problems registered in the refered time stamp.
    dates must be a string in YYYY-MM-dd format (eg. '2015-08-01')"""
    phone_key = 'phone_key'
    if include_phone:
        phone_key = constants.API_PHONE_KEY

    payload = {'start_date': start_date,
               'end_date':   end_date,
               'phone_key':  phone_key}

    r = requests.get(constants.API_END_POINTS['requests'] +
                     '.' +
                     constants.API_RESPONSE_FORMATS['json'],
                     params=payload,
                     allow_redirects=False)
    z_json = str(r.text.decode("utf-8").encode("ascii", "ignore")).strip("'<>()\"` ").replace('\'', '\"')
    json_requests = json.loads(z_json)

    requests_list = []
    for request in json_requests:
        if u'code' in request and request.get('code', default) == 404:
            break

        requests_list.append(request)

    return requests_list


def generate_pdf(template, context, name):
    """Generates PDF files based on given input

    template -- the template filename including the extension
    context -- the context object to be used while rendering the template
    name -- the name to be given to PDF file in disk including the extension
    """

    # Get jinja2 template
    pisa.showLogging()
    env = Environment(loader=PackageLoader('mopa', 'templates'))
    template = env.get_template(template)
    html = template.render(context)

    # Write PDF to file
    f_name = os.path.join(constants.REPORTS_DIR, name)
    with open(f_name, "w+b") as f:
        pisaStatus = pisa.CreatePDF(html, dest=f)

        # Return PDF document for mail sending
        f.seek(0)
        pdf = f.read()
        return pdf


def mail(to, cc, subject, text, attach):
        """Sends email to recepients using credentials provided in
           constants module
           TO-DO: change mailServer call to use with statement"""
        msg = MIMEMultipart()
        msg['From'] = 'MOPA'
        msg['To'] = ', '.join(to)
        msg['Cc'] = ', '.join(cc)
        msg['Subject'] = subject

        msg.attach(MIMEText(text, 'html'))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attach, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(attach))
        msg.attach(part)

        mailServer = smtplib.SMTP(constants.GMAIL_SERVER, constants.GMAIL_PORT)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(constants.GMAIL_USER, constants.GMAIL_PASSWORD)
        mailServer.sendmail('Mopa Notifications', to + cc, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()


class MyJSONEncoder(json.JSONEncoder):
    """JSON Encoder Extensions"""

    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()

    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            try:
                return float(o)
            except:
                return super(DecimalEncoder, self)._iterencode(o, markers)

        if isinstance(o, (date, datetime)):
            return o.isoformat()


class Location(singleton.SingletonMixin):
    """Helper class for all location needs.
    usage: Location.i().method()
    """

    NEIGHBOURHOODS = LOCATIONS = ONLINE_LOCATIONS = None

    def get_locations_tree(self):
        """loads neighbourhoods.json file and returns as a python object."""
        if self.NEIGHBOURHOODS:
            return self.NEIGHBOURHOODS

        data = ""
        with open(name=os.path.join(constants.BASE_DIR,
                                    constants.NEIGHBOURHOODS_JSON_PATH),
                  mode="r") as f:
            for line in f.readlines():
                data = data + line
        self.NEIGHBOURHOODS = json.loads(data)

        return self.NEIGHBOURHOODS

    def get_locations_offline(self):
        """loads locations.json file and converts into a python list"""
        if self.LOCATIONS:
            return self.LOCATIONS

        data = ""
        with open(name=constants.BASE_DIR + '/static/locations.json',
                  mode='r') as f:
            for line in f.readlines():
                data = data + line
        self.LOCATIONS = json.loads(data)

        return self.LOCATIONS

    def get_locations_online(self):
        """loads the locations from the API and converts into a python list"""
        if self.ONLINE_LOCATIONS:
            return self.ONLINE_LOCATIONS

        r = requests.get(constants.API_BASE_URL + "locations.json")
        if r.status_code == 200:
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
            if location[u'location_type'] in [u'container',
                                              u'quarter',
                                              u'critical point']:

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

        district      = xstr(request.get('neighbourhood', default))
        location_name = xstr(request.get('address', default))
        neighbourhood = ''

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

        # No textual location get it from Valter.
        if len(district) == 0 or len(location_name) == 0:
            description = request.get('description', default)
            if description and description.startswith('Criado por USSD'):
                description = description.replace('Criado por USSD. ', '')
                location_name = description

                neighbourhood_text = description.replace('Bairro:', '').strip()
                for c in neighbourhood_text:
                    if c == '.':
                        break
                    neighbourhood = neighbourhood + c

        # No textual location so get it from offline locations
        if len(district) == 0 or len(location_name) == 0:
            location = self.get_location_offline(
                latitude=request.get('lat', default),
                longitude=request.get('long', default)
            )

            district = location['district']
            if not district:
                district = '-'
            if not location_name:
                location_name = location['location_name']
            if not neighbourhood:
                neighbourhood = location['neighbourhood']

        # No textual description so finally get from online from latitude and longitude
        if len(district) == 0 or len(location_name) == 0:
            location = self.get_location_online(
                latitude=request.get('lat', default),
                longitude=request.get('long', default)
            )

            district = location['district']
            if not district:
                district = '-'
            if not location_name:
                location_name = location['location_name']
            if not neighbourhood:
                neighbourhood = location['neighbourhood']

        _return['district'] = district
        _return['location_name'] = location_name
        _return['neighbourhood'] = neighbourhood
        return _return

    def get_monitor(self, _id):
        """Gets a specific monitors details"""
        neighbourhoods = self.get_locations_tree()
        for monitor in neighbourhoods['monitors']:
            if (str(monitor['id']) == str(_id) or
                    int(monitor['id']) == int(_id)):
                return monitor
        return None

    def get_monitors_phones(self):
        """Get the list of all monitors phone numbers"""
        monitor_phones = []
        neighbourhoods = self.get_locations_tree()
        for monitor in neighbourhoods['monitors']:
            if monitor['phone']:
                monitor_phones.append(monitor['phone'])
        return monitor_phones

    def get_notified_person(self, _id):
        """Gets the details of one to be notified"""
        neighbourhoods = self.get_locations_tree()
        for person in neighbourhoods["notified_people"]:
            if str(person["id"]) == str(_id):
                return person
        return None

    def get_monitor_by_phone(self, phone):
        """Gets the details of a monitor using his phone number"""
        neighbourhoods = self.get_locations_tree()
        for monitor in neighbourhoods["monitors"]:
            if str(monitor["phone"]) == str(phone):
                return monitor
        return None

    def get_monitor_point(self, monitor_id):
        """Gets the point data a given monitor"""
        point_data = {}
        neighbourhoods = self.get_locations_tree()
        for district in neighbourhoods["districts"]:
            for neighbourhood in district["neighbourhoods"]:
                for point in neighbourhood["points"]:
                    if (monitor_id in point["monitors"] or
                            str(monitor_id) in point["monitors"]):
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
        neighbourhoods = self.get_locations_tree()
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
