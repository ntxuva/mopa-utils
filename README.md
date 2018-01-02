# Mopa

[![Build Status](https://travis-ci.org/ntxuva/mopa-utils.svg?branch=master)](https://travis-ci.org/ntxuva/mopa-utils)
[![Coverage Status](https://coveralls.io/repos/github/ntxuva/mopa-utils/badge.svg?branch=master)](https://coveralls.io/github/ntxuva/mopa-utils?branch=master)

This project contains the source code for the mopa util. Server side code is written in python and meant to run in python 2.7
To support the project the following external libs have been used

- [Flask](http://flask.pocoo.org/) - for REST API and back-end HTTP
- [Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/) - as ORM for db access
- [Schedule](https://github.com/mrhwick/schedule) - for scheduled tasks
- [Jinja2](http://jinja.pocoo.org/) - For the report templating
- [xhtml2pdf](http://www.xhtml2pdf.com/) - For conversion of html template to html5
- [pudb](https://pypi.python.org/pypi/pudb/) - For debugging

## Installing and Running

```sh
virtualenv venv # create virtual env
source venv/bin/activate # activate virtual env
# pip install -r requirements.txt -t vendor --upgrade # install dependencies in vendor folder. 
# Option above won't work because of https://github.com/pypa/pip/issues/4390
pip install -r requirements.txt --upgrade
pip install gunicorn # install gunicorn WSGI server

python manage.py test # tests
python manage.py runserver # run dev server

gunicorn wsgi # run gunicorn

sudo rm /etc/nginx/sites-enabled/default
sudo cp path-to-mopa-utils/etc/nginx.conf /etc/nginx/sites-available/mopautils # make app available on nginx
sudo ln -s /etc/nginx/sites-available/mopautils /etc/nginx/sites-enabled/mopautils # deploy nginx
sudo service nginx reload

sudo apt-get install supervisord
sudo cp path-to-mopa-utils/etc/supervisord.conf /etc/supervisor/conf.d/mopa-utils.conf
sudo service supervisor restart

cp .env.example .env
# Edit .env then put API_KEY in /etc/environment

# Nuke *.pyc files
sudo find . -name "*.pyc" -exec rm -rf {} \;
sudo find . -name \*.pyc -delete
```

## Guidelines on Common usage of xhtml2pdf and errors

[Pisa and Reportlab pitfalls](http://www.arnebrodowski.de/blog/501-Pisa-and-Reportlab-pitfalls.html)

[Official xhtml2pdf usage guide on github](https://github.com/chrisglass/xhtml2pdf/blob/master/doc/usage.rst)

## Fixing Gmails quirks

The app uses gmail in order to send emails. Gmail by default disables sending email from scripts or programs in order to fix that you need to enable that feature.

The following link shows how: [Allowing less secure apps to access your account](https://support.google.com/accounts/answer/6010255?hl=en)
