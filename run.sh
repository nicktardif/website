pipenv run /bin/bash -c 'export FLASK_APP=web_app; flask db upgrade'
pipenv run /bin/bash -c 'export FLASK_ENV=development; export FLASK_DEBUG=1; gunicorn web_app:app'
