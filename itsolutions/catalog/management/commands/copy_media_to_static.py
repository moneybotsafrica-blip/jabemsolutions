import sys
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Copy media files to staticfiles directory for Vercel deployment'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            source_dir = Path(settings.BASE_DIR) / 'media'
            target_dir = Path(settings.STATIC_ROOT) / 'media'
            
            self.stdout.write(f'Copying media files from {source_dir} to {target_dir}')
            
            if source_dir.exists():
                # Create target directory if it doesn't exist
                target_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy all files from media to staticfiles/media
                copied_count = 0
                for item in source_dir.rglob('*'):
                    if item.is_file():
                        relative_path = item.relative_to(source_dir)
                        target_path = target_dir / relative_path
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, target_path)
                        copied_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'Copied {copied_count} media files to staticfiles'))
            else:
                self.stdout.write(self.style.WARNING('Media directory does not exist'))
        else:
            self.stdout.write('This command is for production only. Skipping in DEBUG mode.')
