#!/bin/bash

NAME="mopa-utils"
PROJECT_DIR=/srv/www/mopa-utils
VIRTUALENV_DIR=/srv/www/mopa-utils/venv
LOG_DIR=/srv/www/mopa-utils/mopa/data/logs/gunicorn
USER=www-data
GROUP=www-data
IP=127.0.0.1
PORT=5000
WORKERS=5

echo "Starting $NAME"

# activate the virtualenv
cd $PROJECT_DIR
source $VIRTUALENV_DIR/bin/activate

# Start your unicorn
exec gunicorn wsgi \
  --bind $IP:$PORT \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=info \
  --reload \
