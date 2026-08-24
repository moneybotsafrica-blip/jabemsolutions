#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'itsolutions'))
django.setup()

from django.core.management import call_command

print("Running Django migrations...")
call_command('migrate', '--noinput')

print("Collecting static files...")
call_command('collectstatic', '--noinput')

print("Build completed successfully!")
