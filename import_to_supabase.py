import os
import sys
import django
import json
from decimal import Decimal

# Setup Django for Supabase
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'itsolutions'))
os.environ['DATABASE_URL'] = 'postgres://postgres.zutlyfpyvssnyostcloa:CwN21WTg2sKasewQ@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product, Category, Brand, Stock
from django.db import transaction

def import_products():
    """Import products to Supabase database"""
    with open('local_products_export.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    print(f'Loaded {len(products_data)} products from export file')
    
    # Get or create categories and brands
    categories = {}
    brands = {}
    
    for product_data in products_data:
        cat_name = product_data['category_name']
        brand_name = product_data['brand_name']
        
        if cat_name not in categories:
            cat, _ = Category.objects.get_or_create(
                slug=cat_name.lower().replace(' ', '-'),
                defaults={'name': cat_name, 'kind': 'hardware'}
            )
            categories[cat_name] = cat
            print(f'Created category: {cat_name}')
        
        if brand_name not in brands:
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            brands[brand_name] = brand
            print(f'Created brand: {brand_name}')
    
    # Import products in small batches
    batch_size = 5  # Very small batches to avoid timeout
    created_count = 0
    updated_count = 0
    
    for i in range(0, len(products_data), batch_size):
        batch = products_data[i:i + batch_size]
        print(f'Processing batch {i//batch_size + 1}/{(len(products_data) + batch_size - 1)//batch_size}')
        
        try:
            with transaction.atomic():
                for product_data in batch:
                    # Check if product exists
                    product = Product.objects.filter(slug=product_data['slug']).first()
                    
                    if product:
                        # Update existing
                        product.name = product_data['name']
                        product.price = Decimal(str(product_data['price']))
                        product.description = product_data['description']
                        product.short_description = product_data['short_description']
                        product.product_type = product_data['product_type']
                        product.is_active = product_data['is_active']
                        product.track_inventory = product_data['track_inventory']
                        product.reorder_level = product_data['reorder_level']
                        product.category = categories[product_data['category_name']]
                        product.brand = brands[product_data['brand_name']]
                        product.save()
                        updated_count += 1
                    else:
                        # Create new
                        product = Product(
                            name=product_data['name'],
                            slug=product_data['slug'],
                            sku=product_data['sku'],
                            price=Decimal(str(product_data['price'])),
                            description=product_data['description'],
                            short_description=product_data['short_description'],
                            product_type=product_data['product_type'],
                            is_active=product_data['is_active'],
                            track_inventory=product_data['track_inventory'],
                            reorder_level=product_data['reorder_level'],
                            category=categories[product_data['category_name']],
                            brand=brands[product_data['brand_name']]
                        )
                        product.save()
                        
                        # Create stock
                        Stock.objects.create(
                            product=product,
                            quantity_on_hand=product_data['stock_quantity'],
                            warehouse_location=product_data['warehouse_location']
                        )
                        created_count += 1
            
            print(f'Batch {i//batch_size + 1} completed')
            
        except Exception as e:
            print(f'Error in batch {i//batch_size + 1}: {str(e)}')
            continue
    
    print(f'\nImport complete:')
    print(f'  Created: {created_count}')
    print(f'  Updated: {updated_count}')

if __name__ == '__main__':
    import_products()