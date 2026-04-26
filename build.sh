#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Building MultiServe application..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if not exists (optional)
# python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

echo "Build completed successfully!"
