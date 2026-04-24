#!/usr/bin/env bash
set -o errexit -o pipefail
pip install -r requirements.txt
python manage.py collectstatic --noinput
