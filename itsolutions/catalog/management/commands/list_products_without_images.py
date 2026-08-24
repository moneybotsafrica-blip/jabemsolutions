import sys
from django.core.management.base import BaseCommand
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'List products without images'

    def handle(self, *args, **options):
        products_without_images = Product.objects.filter(image__isnull=True) | Product.objects.filter(image='')
        
        total_products = Product.objects.count()
        without_images = products_without_images.count()
        with_images = total_products - without_images
        
        self.stdout.write(self.style.SUCCESS(f'Total Products: {total_products}'))
        self.stdout.write(self.style.SUCCESS(f'Products with images: {with_images}'))
        self.stdout.write(self.style.WARNING(f'Products without images: {without_images}'))
        self.stdout.write('')
        
        if without_images > 0:
            self.stdout.write('Products without images:')
            self.stdout.write('-' * 80)
            for product in products_without_images[:100]:  # Limit to first 100
                self.stdout.write(f'ID: {product.id:5} | SKU: {product.sku:20} | Name: {product.name[:60]}')
            
            if without_images > 100:
                self.stdout.write(f'... and {without_images - 100} more')
        else:
            self.stdout.write(self.style.SUCCESS('All products have images!'))
