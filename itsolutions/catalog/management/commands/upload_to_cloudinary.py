import sys
import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from catalog.models import Product
import cloudinary
import cloudinary.uploader

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Upload existing product images to Cloudinary and update database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cloud-name',
            type=str,
            default=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            help='Cloudinary cloud name'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            default=os.environ.get('CLOUDINARY_API_KEY'),
            help='Cloudinary API key'
        )
        parser.add_argument(
            '--api-secret',
            type=str,
            default=os.environ.get('CLOUDINARY_API_SECRET'),
            help='Cloudinary API secret'
        )

    def handle(self, *args, **options):
        cloudinary_url = urlparse(os.environ.get('CLOUDINARY_URL', ''))
        cloud_name = options['cloud_name'] or cloudinary_url.hostname
        api_key = options['api_key'] or cloudinary_url.username
        api_secret = options['api_secret'] or unquote(cloudinary_url.password or '')

        if not all((cloud_name, api_key, api_secret)):
            raise CommandError('Set CLOUDINARY_URL or provide Cloudinary credentials.')

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )

        self.stdout.write('Uploading product images to Cloudinary...')

        products_with_images = Product.objects.exclude(image__isnull=True).exclude(image='').filter(external_image_url='')
        total = products_with_images.count()
        uploaded = 0
        failed = 0

        for product in products_with_images:
            if product.image and product.image.name:
                try:
                    # Get the local file path
                    image_path = Path(settings.MEDIA_ROOT) / product.image.name
                    
                    if image_path.exists():
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            str(image_path),
                            folder='products',
                            public_id=f"products/{product.slug}",
                            overwrite=True
                        )
                        
                        product.external_image_url = result['secure_url']
                        product.save(update_fields=['external_image_url'])
                        
                        uploaded += 1
                        self.stdout.write(f'✓ Uploaded: {product.name[:50]}')
                    else:
                        self.stdout.write(f'✗ File not found: {product.name[:50]}')
                        failed += 1
                        
                except Exception as e:
                    self.stdout.write(f'✗ Error uploading {product.name[:50]}: {str(e)}')
                    failed += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Upload complete:'))
        self.stdout.write(f'  Total products: {total}')
        self.stdout.write(f'  Uploaded: {uploaded}')
        self.stdout.write(f'  Failed: {failed}')
