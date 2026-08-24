import sys
import zipfile
import os
import tempfile
from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from django.utils.text import slugify
from catalog.models import Product, Category, Brand, Stock

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Add Mustek POS products to database with images and descriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            'zip_file',
            type=str,
            help='Path to the mustek_pos_images.zip file'
        )

    def handle(self, *args, **options):
        zip_file = options['zip_file']

        # Product data for Mustek items
        mustek_products = [
            {
                'name': 'Cash Drawer M4052',
                'slug': 'cash-drawer-m4052',
                'sku': 'CD-M4052',
                'price': 15000,
                'product_type': 'hardware',
                'image_file': 'mustek_pos_images/cash_drawer_m4052.png',
                'description': 'M4052 cash drawer with robust construction and secure storage for cash transactions. Features multiple bill and coin compartments, durable metal construction, and compatibility with most POS systems.',
                'keywords': ['cash drawer', 'm4052']
            },
            {
                'name': 'POS Solutions Waiter App',
                'slug': 'pos-solutions-waiter-app',
                'sku': 'POS-WAITER-APP',
                'price': 5000,
                'product_type': 'software',
                'image_file': 'mustek_pos_images/pos_software_waiter_app.webp',
                'description': 'POS Solutions waiter app for mobile order taking and table management in restaurants. Features real-time order synchronization, table management, and payment processing capabilities.',
                'keywords': ['pos software', 'waiter app', 'software']
            },
            {
                'name': 'Cloud-Based POS Software',
                'slug': 'cloud-based-pos-software',
                'sku': 'POS-CLOUD-SOFT',
                'price': 10000,
                'product_type': 'software',
                'image_file': 'mustek_pos_images/pos_software_cloud_based.png',
                'description': 'Cloud-based POS software solution for remote access and real-time business management. Access your business data from anywhere, automatic backups, multi-location support, and comprehensive reporting.',
                'keywords': ['pos software', 'cloud', 'cloud-based', 'software']
            },
            {
                'name': 'POS Head Office Module',
                'slug': 'pos-head-office-module',
                'sku': 'POS-HEAD-OFFICE',
                'price': 15000,
                'product_type': 'software',
                'image_file': 'mustek_pos_images/pos_software_head_office.png',
                'description': 'POS head office module for centralized management of multiple store locations and reporting. Consolidated inventory management, sales analytics, staff performance tracking, and centralized pricing control.',
                'keywords': ['pos software', 'head office', 'head-office', 'software']
            },
            {
                'name': 'POS Payment Integration',
                'slug': 'pos-payment-integration',
                'sku': 'POS-PAYMENT',
                'price': 5000,
                'product_type': 'software',
                'image_file': 'mustek_pos_images/pos_software_payment_icons.png',
                'description': 'POS payment integration supporting multiple payment methods including cards, mobile money, and cash. Seamless integration with M-Pesa, Visa, Mastercard, and other popular payment providers.',
                'keywords': ['pos software', 'payment', 'software']
            },
        ]

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Get or create POS category
                pos_category, _ = Category.objects.get_or_create(
                    slug='pos-hardware',
                    defaults={
                        'name': 'POS Hardware',
                        'kind': 'hardware',
                        'description': 'Point of Sale hardware including terminals, printers, scanners, and accessories.'
                    }
                )

                # Get or create software category
                software_category, _ = Category.objects.get_or_create(
                    slug='pos-software',
                    defaults={
                        'name': 'POS Software',
                        'kind': 'software',
                        'description': 'Point of Sale software solutions for retail and hospitality businesses.'
                    }
                )

                # Get or create brand
                brand, _ = Brand.objects.get_or_create(
                    name='Jabem Solutions'
                )

                created_count = 0
                updated_count = 0

                for product_data in mustek_products:
                    # Check if product already exists
                    product = Product.objects.filter(slug=product_data['slug']).first()
                    
                    if product:
                        # Update existing product
                        self.stdout.write(f'Updating existing product: {product_data["name"]}')
                        updated_count += 1
                    else:
                        # Create new product
                        product = Product(
                            name=product_data['name'],
                            slug=product_data['slug'],
                            sku=product_data['sku'],
                            price=product_data['price'],
                            product_type=product_data['product_type'],
                            description=product_data['description'],
                            short_description=product_data['description'][:255],
                            is_active=True,
                            track_inventory=True,
                            reorder_level=5
                        )
                        created_count += 1

                    # Set category based on product type
                    if product_data['product_type'] == 'hardware':
                        product.category = pos_category
                        product.brand = brand
                    else:
                        product.category = software_category

                    # Save product
                    product.save()

                    # Create stock record if needed
                    if not hasattr(product, 'stock'):
                        Stock.objects.create(
                            product=product,
                            quantity_on_hand=10,
                            warehouse_location='Main Store'
                        )

                    # Add image
                    image_file = product_data['image_file']
                    if image_file in [f.filename for f in zip_ref.filelist]:
                        self.add_image_to_product(product, zip_ref, image_file)

                self.stdout.write(self.style.SUCCESS(f'\nProduct import complete:'))
                self.stdout.write(f'  Created: {created_count}')
                self.stdout.write(f'  Updated: {updated_count}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing: {str(e)}'))

    def add_image_to_product(self, product, zip_ref, image_path):
        """Add image from zip to product"""
        try:
            file_data = zip_ref.read(image_path)
            filename = os.path.basename(image_path)
            ext = os.path.splitext(filename)[1].lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                temp_file.write(file_data)
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    product.image.save(
                        f"{product.slug}{ext}",
                        File(f),
                        save=True
                    )
                self.stdout.write(f'  Added image: {filename}')
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  Error adding image: {str(e)}'))
