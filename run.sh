mkdir -p $PWD/web_app/static/data/ # Create working folder for data

pipenv run /bin/bash -c 'export FLASK_APP=web_app; flask db upgrade'
if [[ $1 = "DEBUG" ]]; then
pipenv run /bin/bash -c 'export FLASK_ENV=development; export FLASK_DEBUG=1; export FLASK_APP=web_app:app; flask run -p 8000'
else
pipenv run /bin/bash -c 'export FLASK_DEBUG=1; gunicorn web_app:app'
fi
