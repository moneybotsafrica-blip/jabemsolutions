import sys
from django.core.management.base import BaseCommand
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Check for Glantix references in product names and descriptions'

    def handle(self, *args, **options):
        self.stdout.write('Checking for Glantix references in product names...')
        self.stdout.write('=' * 80)
        
        products_with_glantix = Product.objects.filter(name__icontains='glantix')
        self.stdout.write(f'Products with "glantix" in name: {products_with_glantix.count()}')
        
        if products_with_glantix.exists():
            for product in products_with_glantix[:10]:
                self.stdout.write(f'  - {product.name[:80]}')
        
        self.stdout.write('')
        self.stdout.write('Checking for Glantix references in descriptions...')
        self.stdout.write('=' * 80)
        
        products_with_glantix_desc = Product.objects.filter(description__icontains='glantix')
        self.stdout.write(f'Products with "glantix" in description: {products_with_glantix_desc.count()}')
        
        if products_with_glantix_desc.exists():
            for product in products_with_glantix_desc[:10]:
                self.stdout.write(f'  - {product.name[:80]}')
                self.stdout.write(f'    Desc: {product.description[:100]}...')
        
        self.stdout.write('')
        self.stdout.write('Checking for phone number patterns in names...')
        self.stdout.write('=' * 80)
        
        import re
        phone_pattern = r'\d{3,4}\s*\d{3,7}'
        products_with_phones = []
        for product in Product.objects.all()[:100]:
            if re.search(phone_pattern, product.name):
                products_with_phones.append(product)
        
        self.stdout.write(f'Products with phone patterns in name (first 100): {len(products_with_phones)}')
        for product in products_with_phones[:10]:
            self.stdout.write(f'  - {product.name[:80]}')
