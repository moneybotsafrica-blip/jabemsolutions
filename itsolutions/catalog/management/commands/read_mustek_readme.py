import sys
import zipfile
from django.core.management.base import BaseCommand

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Read README.md from mustek_pos_images.zip'

    def add_arguments(self, parser):
        parser.add_argument(
            'zip_file',
            type=str,
            help='Path to the mustek_pos_images.zip file'
        )

    def handle(self, *args, **options):
        zip_file = options['zip_file']

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                readme_file = 'mustek_pos_images/README.md'
                if readme_file in [f.filename for f in zip_ref.filelist]:
                    content = zip_ref.read(readme_file).decode('utf-8')
                    self.stdout.write('README.md content:')
                    self.stdout.write('=' * 80)
                    self.stdout.write(content)
                else:
                    self.stdout.write('README.md not found in zip')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading zip file: {str(e)}'))
