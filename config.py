import os

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Admin Emails
ADMINS = frozenset(['admin@localhost'])

# Define the database
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "ntxuva"
DB_USER = "root"
DB_PASSWORD = ""

SQLALCHEMY_ECHO = DEBUG
SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://%s:%s@%s:%s/%s" % \
    (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2  # 8

# WTF Forms Setting
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "secret"

# Enable protection against *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"
