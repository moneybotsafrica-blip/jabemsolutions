import sys
import zipfile
from django.core.management.base import BaseCommand

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Examine the structure of mustek_pos_images.zip'

    def add_arguments(self, parser):
        parser.add_argument(
            'zip_file',
            type=str,
            help='Path to the mustek_pos_images.zip file'
        )

    def handle(self, *args, **options):
        zip_file = options['zip_file']

        if not zip_file:
            zip_file = r'C:\Users\Moneybots\Downloads\jabee-solutions\mustek_pos_images.zip'

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                self.stdout.write(f'Examining: {zip_file}')
                self.stdout.write('=' * 80)
                self.stdout.write(f'Total files in zip: {len(zip_ref.filelist)}')
                self.stdout.write('')
                
                # List first 20 files
                self.stdout.write('First 20 files:')
                for i, file_info in enumerate(zip_ref.filelist[:20]):
                    self.stdout.write(f'  {file_info.filename}')
                
                if len(zip_ref.filelist) > 20:
                    self.stdout.write(f'  ... and {len(zip_ref.filelist) - 20} more files')
                
                self.stdout.write('')
                
                # Look for JSON or CSV files
                self.stdout.write('Looking for data files (JSON/CSV):')
                data_files = [f for f in zip_ref.filelist if f.filename.lower().endswith(('.json', '.csv'))]
                if data_files:
                    for file_info in data_files:
                        self.stdout.write(f'  Found: {file_info.filename}')
                        # Try to read the first few lines
                        try:
                            content = zip_ref.read(file_info.filename).decode('utf-8')[:500]
                            self.stdout.write(f'  Content preview: {content[:200]}...')
                        except:
                            pass
                else:
                    self.stdout.write('  No JSON or CSV files found')
                
                self.stdout.write('')
                
                # Look for image files
                self.stdout.write('Looking for image files:')
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
                image_files = [f for f in zip_ref.filelist if any(f.filename.lower().endswith(ext) for ext in image_extensions)]
                self.stdout.write(f'  Total image files: {len(image_files)}')
                
                if image_files:
                    # Show some sample image paths
                    self.stdout.write('  Sample image paths:')
                    for file_info in image_files[:10]:
                        self.stdout.write(f'    {file_info.filename}')
                
                self.stdout.write('')
                
                # Check directory structure
                self.stdout.write('Directory structure:')
                dirs = set()
                for file_info in zip_ref.filelist:
                    parts = file_info.filename.split('/')
                    if len(parts) > 1:
                        dirs.add('/'.join(parts[:-1]))
                
                for d in sorted(list(dirs))[:20]:
                    self.stdout.write(f'  {d}/')
                
                if len(dirs) > 20:
                    self.stdout.write(f'  ... and {len(dirs) - 20} more directories')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading zip file: {str(e)}'))
