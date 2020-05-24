#!/usr/bin/env bash
pipenv run /bin/bash -c 'export FLASK_APP=web_app; export FLASK_CONFIG=testing; flask db upgrade; nose2'
