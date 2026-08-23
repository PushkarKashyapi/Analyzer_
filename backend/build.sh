#!/usr/bin/env bash
set -o errexit

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput
