#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies with no cache to reduce memory usage
pip install --upgrade pip --no-cache-dir
pip install -r requirements.txt --no-cache-dir

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
