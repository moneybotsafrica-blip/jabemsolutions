import sys
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Check product image paths and file existence'

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        
        self.stdout.write(f'MEDIA_ROOT: {media_root}')
        self.stdout.write(f'MEDIA_ROOT exists: {media_root.exists()}')
        self.stdout.write('')
        
        products_with_images = Product.objects.exclude(image__isnull=True).exclude(image='')
        self.stdout.write(f'Products with images in database: {products_with_images.count()}')
        self.stdout.write('')
        
        missing_count = 0
        found_count = 0
        
        for product in products_with_images[:20]:  # Check first 20
            image_path = product.image.name if product.image else None
            if image_path:
                full_path = media_root / image_path
                exists = full_path.exists()
                
                if exists:
                    found_count += 1
                    self.stdout.write(f'✓ {product.name[:50]}: {image_path}')
                else:
                    missing_count += 1
                    self.stdout.write(f'✗ {product.name[:50]}: {image_path} (MISSING)')
        
        self.stdout.write('')
        self.stdout.write(f'Found: {found_count}')
        self.stdout.write(f'Missing: {missing_count}')
        
        # Check what's actually in media directory
        self.stdout.write('')
        self.stdout.write('Actual files in media directory:')
        if media_root.exists():
            file_count = 0
            for file_path in media_root.rglob('*'):
                if file_path.is_file():
                    self.stdout.write(f'  {file_path.relative_to(media_root)}')
                    file_count += 1
                    if file_count >= 30:
                        self.stdout.write('  ... (showing first 30 files)')
                        break
            if file_count == 0:
                self.stdout.write('  No files found in media directory')
        else:
            self.stdout.write('  Media directory does not exist')
