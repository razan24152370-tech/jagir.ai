#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Installing dependencies..."
# Install dependencies with no cache to reduce memory usage
pip install --upgrade pip --no-cache-dir
pip install -r requirements.txt --no-cache-dir

echo "==> Running database migrations..."
# Run migrations (this creates all database tables)
python manage.py migrate --no-input

echo "==> Collecting static files..."
# Ensure staticfiles directory exists
mkdir -p staticfiles
# Collect static files with verbose output
python manage.py collectstatic --no-input --clear --no-post-process

echo "==> Creating/Updating Admin User..."
# Create admin user automatically
python create_admin.py

echo "==> Build complete!"
