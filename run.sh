#!/bin/bash

mkdir -p $PWD/web_app/static/data/ # Create working folder for data

SECRETS=$(cat secrets);

pipenv run /bin/bash -c "${SECRETS} export FLASK_APP=web_app; flask db upgrade"
if [[ $1 = "DEBUG" ]]; then
pipenv run /bin/bash -c "${SECRETS} export FLASK_ENV=development; export FLASK_DEBUG=1; export FLASK_APP=web_app:app; flask run -p 8000"
else
pipenv run /bin/bash -c "${SECRETS} export FLASK_DEBUG=1; gunicorn -w 3 --threads 12 --bind unix:/tmp/nicktardif.sock --group www-data web_app:app -t 1800 --access-logfile -"
fi
