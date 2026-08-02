#!/bin/bash
set -e

python3 -m pip install --disable-pip-version-check --break-system-packages -r requirements.txt
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput

mkdir -p staticfiles_build
cp -R staticfiles/. staticfiles_build/ 2>/dev/null || true
cp -R static/. staticfiles_build/ 2>/dev/null || true
