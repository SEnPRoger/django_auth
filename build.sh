#!/usr/bin/env bash

set -o errexit  # exit on error

pip install -r requirements.txt

mkdir -p /opt/render/project/src/static

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate