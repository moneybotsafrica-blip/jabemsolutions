import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'itsolutions'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product, Category, Brand, Stock
from decimal import Decimal

def export_products():
    """Export products from local database"""
    products_data = []
    
    # Get default category and brand
    default_category = Category.objects.filter(slug='general').first()
    default_brand = Brand.objects.filter(name='Jabem Solutions').first()
    
    for product in Product.objects.all():
        product_dict = {
            'name': product.name,
            'slug': product.slug,
            'sku': product.sku,
            'price': float(product.price),
            'description': product.description,
            'short_description': product.short_description,
            'product_type': product.product_type,
            'is_active': product.is_active,
            'track_inventory': product.track_inventory,
            'reorder_level': product.reorder_level,
            'category_name': product.category.name if product.category else 'General',
            'brand_name': product.brand.name if product.brand else 'Jabem Solutions',
        }
        
        # Add stock info
        if hasattr(product, 'stock'):
            product_dict['stock_quantity'] = product.stock.quantity_on_hand
            product_dict['warehouse_location'] = product.stock.warehouse_location
        else:
            product_dict['stock_quantity'] = 10
            product_dict['warehouse_location'] = 'Main Store'
            
        products_data.append(product_dict)
    
    with open('local_products_export.json', 'w', encoding='utf-8') as f:
        json.dump(products_data, f, indent=2, ensure_ascii=False)
    
    print(f'Exported {len(products_data)} products to local_products_export.json')
    return products_data

if __name__ == '__main__':
    export_products()