import os
import sys
import django
import json
import re

# Setup Django for Supabase
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'itsolutions'))
os.environ['DATABASE_URL'] = 'postgres://postgres.zutlyfpyvssnyostcloa:CwN21WTg2sKasewQ@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product

def update_product_images():
    """Update products with their external image URLs from JSON file"""
    with open('products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    
    print(f'Loaded {len(products_data)} products from JSON file')
    
    # First, add external_image_url field to model if it doesn't exist
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE catalog_product 
                ADD COLUMN IF NOT EXISTS external_image_url VARCHAR(500);
            """)
        print('Added external_image_url column to database')
    except Exception as e:
        print(f'Column might already exist or error: {e}')
    
    updated_count = 0
    skipped_count = 0
    
    for product_data in products_data:
        # Skip products with invalid names
        if not product_data.get('name') or product_data['name'] in [',', '.']:
            skipped_count += 1
            continue
        
        # Clean the product name
        name = product_data['name']
        name = re.sub(r'^0700 \d{6} \| Buy ', '', name).strip()
        
        if not name:
            skipped_count += 1
            continue
        
        # Get the slug
        slug = product_data.get('slug')
        if not slug:
            skipped_count += 1
            continue
        
        # Find the product
        product = Product.objects.filter(slug=slug).first()
        if not product:
            skipped_count += 1
            continue
        
        # Get the image URL
        image_urls = product_data.get('image_urls', '')
        if not image_urls:
            skipped_count += 1
            continue
        
        # Extract the first image URL (they're separated by |)
        first_image_url = image_urls.split('|')[0].strip()
        
        if not first_image_url or first_image_url == 'https://glantix.co.ke/images/install.jpeg':
            skipped_count += 1
            continue
        
        # Update the product with external image URL
        product.external_image_url = first_image_url
        product.save(update_fields=['external_image_url'])
        
        updated_count += 1
        print(f'Updated image URL for: {name}')
    
    print(f'\nImage URL update complete:')
    print(f'  Updated: {updated_count}')
    print(f'  Skipped: {skipped_count}')

if __name__ == '__main__':
    update_product_images()