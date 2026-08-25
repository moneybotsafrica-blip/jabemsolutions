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

print("Loading local data...")
try:
    # Load data with ignorenonexistent to handle any model differences
    call_command('loaddata', 'local_data.json', '--ignorenonexistent')
    print("Local data loaded successfully!")
except Exception as e:
    print(f"Local data loading completed (may have existing data): {e}")

print("Populating POS demo data...")
try:
    call_command('populate_pos_demo')
except Exception as e:
    print(f"POS demo population completed (may have existing data): {e}")

print("Collecting static files...")
call_command('collectstatic', '--noinput')

# Copy static files to public directory for Vercel deployment
staticfiles_dir = os.path.join(itsolutions_dir, 'staticfiles')
public_dir = os.path.join(current_dir, 'public')

if os.path.exists(staticfiles_dir):
    print("Copying static files to public directory for Vercel deployment...")
    import shutil
    
    # Remove existing public directory if it exists
    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
    
    # Copy entire staticfiles directory to public
    shutil.copytree(staticfiles_dir, public_dir)
    print("Static files copied to public directory successfully!")
else:
    print("No staticfiles directory found, skipping copy.")

# Copy media files to static files for Vercel deployment
media_dir = os.path.join(itsolutions_dir, 'media')
static_dir = os.path.join(itsolutions_dir, 'staticfiles')

if os.path.exists(media_dir):
    print("Copying media files to static files for Vercel deployment...")
    media_files_count = 0
    
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, media_dir)
            dest_path = os.path.join(static_dir, 'media', relative_path)
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            media_files_count += 1
            if media_files_count <= 10:
                print(f"Copied: {relative_path}")
    
    print(f"Total media files copied: {media_files_count}")
    print("Media files copied successfully!")
    
    # Recopy to public directory to ensure media files are included
    public_media_dir = os.path.join(public_dir, 'media')
    if os.path.exists(static_dir):
        media_source_dir = os.path.join(static_dir, 'media')
        if os.path.exists(media_source_dir):
            print("Copying media files to public directory...")
            if os.path.exists(public_media_dir):
                shutil.rmtree(public_media_dir)
            shutil.copytree(media_source_dir, public_media_dir)
            print("Media files copied to public directory successfully!")
else:
    print("No media directory found, skipping media file copy.")

print("Build completed successfully!")
