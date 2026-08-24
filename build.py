#!/usr/bin/env python
import os
import sys
import shutil

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

print("Populating POS demo data...")
try:
    call_command('populate_pos_demo')
except Exception as e:
    print(f"POS demo population completed (may have existing data): {e}")

print("Collecting static files...")
call_command('collectstatic', '--noinput')

# Copy media files to static files for Vercel deployment
media_dir = os.path.join(itsolutions_dir, 'media')
static_dir = os.path.join(itsolutions_dir, 'staticfiles')

if os.path.exists(media_dir):
    print("Copying media files to static files for Vercel deployment...")
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, media_dir)
            dest_path = os.path.join(static_dir, 'media', relative_path)
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            print(f"Copied: {relative_path}")
    
    print("Media files copied successfully!")
else:
    print("No media directory found, skipping media file copy.")

print("Build completed successfully!")
