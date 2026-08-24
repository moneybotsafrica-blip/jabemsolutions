#!/bin/bash
set -e

echo "Running Django migrations..."
python itsolutions/manage.py migrate --noinput

echo "Collecting static files..."
python itsolutions/manage.py collectstatic --noinput

echo "Build completed successfully!"
