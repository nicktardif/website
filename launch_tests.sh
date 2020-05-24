#!/usr/bin/env bash
pipenv run /bin/bash -c 'export FLASK_APP=web_app; flask db upgrade'
pipenv run nose2
