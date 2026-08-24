import json
import sys
import os
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from catalog.models import Product, Category, Brand, Stock

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Import products from products.json file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the products.json file'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                products_data = json.load(f)

            self.stdout.write(f'Found {len(products_data)} products in JSON file')

            # Get or create default category
            default_category, _ = Category.objects.get_or_create(
                slug='general',
                defaults={
                    'name': 'General',
                    'kind': 'hardware',
                    'description': 'General products'
                }
            )

            # Get or create default brand
            default_brand, _ = Brand.objects.get_or_create(
                name='Jabem Solutions'
            )

            created_count = 0
            updated_count = 0
            skipped_count = 0
            batch_size = 10  # Very small batches to avoid timeout

            for i in range(0, len(products_data), batch_size):
                batch = products_data[i:i + batch_size]
                self.stdout.write(f'Processing batch {i//batch_size + 1}/{(len(products_data) + batch_size - 1)//batch_size} ({len(batch)} products)')
                
                for product_data in batch:
                        # Skip products with invalid names
                        if not product_data.get('name') or product_data['name'] in [',', '.']:
                            skipped_count += 1
                            continue

                        # Clean the product name
                        name = product_data['name']
                        # Remove phone number prefix if present
                        name = re.sub(r'^0700 \d{6} \| Buy ', '', name)
                        name = name.strip()

                        if not name:
                            skipped_count += 1
                            continue

                        # Generate or use existing slug
                        slug = product_data.get('slug', slugify(name))

                        # Parse price
                        price = self.parse_price(product_data.get('price', '0'))

                        # Extract description
                        description = product_data.get('description', '')

                        # Generate unique SKU if not present
                        sku = product_data.get('sku')
                        if not sku:
                            # Generate a unique SKU based on slug
                            base_sku = f'JAB-{slug[:8].upper()}'
                            counter = 1
                            sku = base_sku
                            while Product.objects.filter(sku=sku).exists():
                                sku = f'{base_sku}-{counter}'
                                counter += 1

                        # Check if product already exists
                        product = Product.objects.filter(slug=slug).first()

                        if product:
                            # Update existing product
                            self.stdout.write(f'Updating existing product: {name}')
                            product.name = name
                            product.price = price
                            product.description = description
                            product.short_description = description[:255] if description else ''
                            product.save()
                            updated_count += 1
                        else:
                            # Create new product
                            product = Product(
                                name=name,
                                slug=slug,
                                sku=sku,
                                category=default_category,
                                brand=default_brand,
                                price=price,
                                product_type='hardware',
                                description=description,
                                short_description=description[:255] if description else '',
                                is_active=True,
                                track_inventory=True,
                                reorder_level=5
                            )
                            product.save()
                            created_count += 1

                            # Create stock record
                            Stock.objects.create(
                                product=product,
                                quantity_on_hand=10,
                                warehouse_location='Main Store'
                            )

                            self.stdout.write(f'Created product: {name}')

                self.stdout.write(f'Batch {i//batch_size + 1} completed')

            self.stdout.write(self.style.SUCCESS(f'\nProduct import complete:'))
            self.stdout.write(f'  Created: {created_count}')
            self.stdout.write(f'  Updated: {updated_count}')
            self.stdout.write(f'  Skipped: {skipped_count}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing: {str(e)}'))
            import traceback
            traceback.print_exc()

    def parse_price(self, price_string):
        """Parse price string like 'KSH 15,000 (KSH 17,400 inc VAT)' to decimal"""
        try:
            # Extract the first price value (before VAT)
            match = re.search(r'KSH\s*([\d,]+(?:\.\d+)?)', price_string)
            if match:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
            return 0.0
        except (ValueError, AttributeError):
            return 0.0