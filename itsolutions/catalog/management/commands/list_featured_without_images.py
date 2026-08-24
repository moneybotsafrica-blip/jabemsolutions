import sys
from django.core.management.base import BaseCommand
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'List featured products without images'

    def handle(self, *args, **options):
        featured_products = Product.objects.filter(is_active=True)[:6]
        
        self.stdout.write('Featured Products (first 6 active products):')
        self.stdout.write('=' * 80)
        
        without_images = []
        
        for product in featured_products:
            has_image = bool(product.image)
            status = '✓' if has_image else '✗'
            self.stdout.write(f'{status} ID: {product.id:5} | SKU: {product.sku:20} | Name: {product.name[:60]}')
            if not has_image:
                without_images.append(product)
        
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total featured products: {len(featured_products)}')
        self.stdout.write(f'Featured products without images: {len(without_images)}')
        
        if without_images:
            self.stdout.write(self.style.WARNING('\nFeatured products missing images:'))
            for product in without_images:
                self.stdout.write(f'  - {product.name} (SKU: {product.sku})')
        else:
            self.stdout.write(self.style.SUCCESS('\nAll featured products have images!'))
