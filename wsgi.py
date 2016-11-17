# -*- coding: utf-8 -*-

import os
import sys

sys.dont_write_bytecode = True

if os.environ.get('WORKER_CLASS') in ('greenlet', 'gevent'):
    # Monkey-patching for gevent.
    from gevent import monkey; monkey.patch_all()

# Redirect print statements
# http://serverfault.com/questions/239614/wsgi-and-python-print-statements#239621
sys.stdout = sys.stderr

# Fix path
path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.append(path)
os.chdir(path)

# import all library code and application packages
sys.path.append(path + '/vendor')
sys.path.append(path + '/mopa')
from mopa import create_app

def wsgi_app(environ, start_response):
    import sys
    output = sys.version.encode('utf8')
    status = '200 OK'
    headers = [('Content-type', 'text/plain'),
               ('Content-Length', str(len(output)))]
    start_response(status, headers)
    yield output


# mod_wsgi need the *application* variable to serve our small app
# application = wsgi_app
application = create_app()
