import os
import sys
import django

sys.path.insert(0, r'c:\Users\Moneybots\Downloads\jabee-solutions\itsolutions')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product

product = Product.objects.filter(name__icontains='POS Terminal Pro').first()
if product:
    print(f'Product: {product.name}')
    print(f'Image URL: {product.get_image_url()}')
    print(f'External URL: {product.external_image_url}')
    print(f'Has image field: {product.image.name if product.image else "No"}')
else:
    print('Product not found')
