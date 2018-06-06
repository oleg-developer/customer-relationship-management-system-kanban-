#!/usr/bin/env bash

python manage.py migrate
uwsgi --yaml uwsgi.yml