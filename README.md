# Mopa

This project contains the source code for the mopa util. Server side code is written in python and meant to run in python 2.7
To support the project the following external libs have been used
- [flask](http://flask.pocoo.org/) - for REST API and backend HTTP
- [flask-sqlalchemy](https://pythonhosted.org/Flask-SQLAlchemy/) - as ORM for db access
- [Schedule](https://github.com/mrhwick/schedule) - for scheduled tasks
- [Jinja2](http://jinja.pocoo.org/) - For the report templating
- [xhtml2pdf](http://www.xhtml2pdf.com/) - For convertion of html template to html5
- [pudb](https://pypi.python.org/pypi/pudb/) - For debugging

## Installing and Running:
1. For debian/linux deployment install python dev and setup tools - `apt-get install python-dev python-setuptools`
2. create a new virtual environment using `virtualenv`. 
	Activate it `source virtual_env_path/din/activate`. 
	`cd` into it and install the dependencies based on `requirements.txt` file - `pip install -r requirements.txt`
3. cd into dev folder where the actual code lives and run the 'run' module like a normal python program `python run.py`

## Guidelines on Common usage of xhtml2pdf and errors
[Pisa and Reportlab pitfalls](http://www.arnebrodowski.de/blog/501-Pisa-and-Reportlab-pitfalls.html)

[Official xhtml2pdf usage guide on github](https://github.com/chrisglass/xhtml2pdf/blob/master/doc/usage.rst)

## About SSH and command line run programs
Since the app must be started from command line and we're accessing the server remotely via SSH, when we run it we *must* start it with nohup (Example: `nohup python run.py`), so it can continue running when we close the terminal session.
Yes, there are other alternatives so on, but this is the solution that worked for us.

## Fixing Gmails quirks
The app uses gmail in order to send emails. Gmail by default disables sending email from scripts or programs in order to fix that you need to enable that feature.

The following link shows how: [Allowing less secure apps to access your account](https://support.google.com/accounts/answer/6010255?hl=en)

## Debugging and Testing
python -m pudb.run test-run.py