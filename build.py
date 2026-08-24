#!/usr/bin/env python
import os
import sys

# Add the itsolutions directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
itsolutions_dir = os.path.join(current_dir, 'itsolutions')
if itsolutions_dir not in sys.path:
    sys.path.insert(0, itsolutions_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command

print("Running Django migrations...")
call_command('migrate', '--noinput')

print("Collecting static files...")
call_command('collectstatic', '--noinput')

print("Build completed successfully!")
