import sys
import zipfile
import os
import tempfile
from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Import Mustek POS images and match to existing products'

    def add_arguments(self, parser):
        parser.add_argument(
            'zip_file',
            type=str,
            help='Path to the mustek_pos_images.zip file'
        )

    def handle(self, *args, **options):
        zip_file = options['zip_file']

        # Image mapping from README
        image_mapping = {
            'mustek_pos_images/pos_terminal_15inch.jpg': {
                'keywords': ['posiflex', 'fanfree', '15-inch', '15 inch', 'terminal', 'pos terminal'],
                'description': 'Posiflex FANFREE 15-inch POS terminal with TFT LCD display. High-quality touch screen for efficient point of sale operations.'
            },
            'mustek_pos_images/receipt_printer_epson_tmt88vii_back.webp': {
                'keywords': ['epson', 'tm-t88vii', 'tm t88vii', 'receipt printer', 'thermal printer'],
                'description': 'Epson TM-T88VII high-speed thermal receipt printer with USB, Ethernet, and PowerUSB connectivity. Rear view showing connectivity options.'
            },
            'mustek_pos_images/receipt_printer_epson_tmt88vii_left.webp': {
                'keywords': ['epson', 'tm-t88vii', 'tm t88vii', 'receipt printer', 'thermal printer'],
                'description': 'Epson TM-T88VII high-speed thermal receipt printer with USB, Ethernet, and PowerUSB connectivity. Side view showing compact design.'
            },
            'mustek_pos_images/receipt_printer_epson_tmt88vii_front.webp': {
                'keywords': ['epson', 'tm-t88vii', 'tm t88vii', 'receipt printer', 'thermal printer'],
                'description': 'Epson TM-T88VII high-speed thermal receipt printer with USB, Ethernet, and PowerUSB connectivity. Front view showing paper output.'
            },
            'mustek_pos_images/barcode_scanner_posiflex_ts2200ub.jpg': {
                'keywords': ['posiflex', 'ts-2200u-b', 'ts2200ub', 'barcode scanner', 'scanner'],
                'description': 'Posiflex TS-2200U-B omni-directional barcode scanner for fast and accurate product scanning at checkout.'
            },
            'mustek_pos_images/cash_drawer_m4052.png': {
                'keywords': ['cash drawer', 'm4052'],
                'description': 'M4052 cash drawer with robust construction and secure storage for cash transactions.'
            },
            'mustek_pos_images/pos_software_waiter_app.webp': {
                'keywords': ['pos software', 'waiter app', 'software'],
                'description': 'POS Solutions waiter app for mobile order taking and table management in restaurants.'
            },
            'mustek_pos_images/pos_software_cloud_based.png': {
                'keywords': ['pos software', 'cloud', 'cloud-based', 'software'],
                'description': 'Cloud-based POS software solution for remote access and real-time business management.'
            },
            'mustek_pos_images/pos_software_head_office.png': {
                'keywords': ['pos software', 'head office', 'head-office', 'software'],
                'description': 'POS head office module for centralized management of multiple store locations and reporting.'
            },
            'mustek_pos_images/pos_software_payment_icons.png': {
                'keywords': ['pos software', 'payment', 'software'],
                'description': 'POS payment integration supporting multiple payment methods including cards, mobile money, and cash.'
            },
        }

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                updated_count = 0
                skipped_count = 0
                
                for image_path, mapping in image_mapping.items():
                    if image_path not in [f.filename for f in zip_ref.filelist]:
                        self.stdout.write(f'Image not found in zip: {image_path}')
                        continue
                    
                    # Find matching product
                    matched_product = self.find_matching_product(mapping['keywords'])
                    
                    if matched_product:
                        # Update product with image and description
                        self.update_product_with_image(matched_product, zip_ref, image_path, mapping['description'])
                        updated_count += 1
                        self.stdout.write(f'Updated: {matched_product.name} with {os.path.basename(image_path)}')
                    else:
                        skipped_count += 1
                        self.stdout.write(f'No match found for: {os.path.basename(image_path)}')
                
                self.stdout.write(self.style.SUCCESS(f'\nImport complete:'))
                self.stdout.write(f'  Updated: {updated_count}')
                self.stdout.write(f'  Skipped: {skipped_count}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing zip file: {str(e)}'))

    def find_matching_product(self, keywords):
        """Find a product that matches the given keywords"""
        for product in Product.objects.filter(is_active=True):
            product_text = f"{product.name} {product.description} {product.sku}".lower()
            # Check if at least 2 keywords match
            matches = sum(1 for keyword in keywords if keyword.lower() in product_text)
            if matches >= 2:
                return product
        return None

    def update_product_with_image(self, product, zip_ref, image_path, description):
        """Update product with image from zip and description"""
        try:
            with transaction.atomic():
                # Read image from zip
                file_data = zip_ref.read(image_path)
                
                # Determine file extension
                filename = os.path.basename(image_path)
                ext = os.path.splitext(filename)[1].lower()
                
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                    temp_file.write(file_data)
                    temp_file_path = temp_file.name
                
                try:
                    # Open the temp file and save to product
                    with open(temp_file_path, 'rb') as f:
                        product.image.save(
                            f"{product.slug}{ext}",
                            File(f),
                            save=True
                        )
                    
                    # Update description
                    if description:
                        product.description = description
                        product.short_description = description[:255]
                        product.save()
                        
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating product {product.name}: {str(e)}'))
