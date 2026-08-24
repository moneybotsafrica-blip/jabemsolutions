import sys
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Remove Glantix references from product names and descriptions'

    def handle(self, *args, **options):
        updated_count = 0
        skipped_count = 0
        
        for product in Product.objects.all():
            try:
                with transaction.atomic():
                    name_updated = False
                    desc_updated = False
                    
                    # Clean product name - more comprehensive patterns
                    original_name = product.name
                    cleaned_name = original_name
                    
                    # Remove various Glantix patterns
                    patterns = [
                        r'\|\s*[Gg]lantix[^\|]*',  # | Glantix...
                        r'[Gg]lantix[^\|]*\|',  # Glantix... |
                        r'\|\s*[Gg]lantix$',  # | Glantix at end
                        r'^[Gg]lantix[^\|]*\|',  # Glantix... | at start
                        r'[Gg]lantixn\s*\|',  # Glantixn |
                        r'[Gg]lantix;\s*',  # Glantix;
                        r'\|\s*[Gg]lantix',  # | Glantix
                        r'at\s+[Gg]lantix',  # at Glantix
                        r'Best Price at [Gg]lantix',  # Best Price at Glantix
                        r'[Gg]lantix:\s*\d+',  # Glantix:0700...
                        r'[Gg]lantix\.\s*\d+',  # Glantix.0700...
                        r'[Gg]lantix:\s*\d+\.\s*',  # Glantix:0731.
                        r':\s*[Gg]lantix',  # :Glantix
                        r'[Gg]lantix\s*$',  # Glantix at end
                        r'\s+[Gg]lantix\s+',  # Glantix in middle
                        r'^[Gg]lantix:\s*Buy\s+',  # Glantix: Buy
                        r'^[Gg]lantix:\s*',  # Glantix: at start
                    ]
                    
                    for pattern in patterns:
                        cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
                    
                    # Remove phone numbers
                    cleaned_name = re.sub(r'^\d{3,4}\s*\d{3,7}\s*\|', '', cleaned_name)
                    cleaned_name = re.sub(r'\|\s*\d{3,4}\s*\d{3,7}', '', cleaned_name)
                    cleaned_name = re.sub(r'\|\s*\d{3,4}\s*\d{3,7}\s*\|', '', cleaned_name)
                    
                    # Remove "Buy" prefix
                    cleaned_name = re.sub(r'^Buy\s+', '', cleaned_name, flags=re.IGNORECASE)
                    
                    # Clean up extra spaces and pipes
                    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
                    cleaned_name = re.sub(r'\s*\|\s*', ' | ', cleaned_name)
                    cleaned_name = cleaned_name.strip(' |')
                    
                    if cleaned_name and cleaned_name != original_name:
                        product.name = cleaned_name
                        name_updated = True
                    
                    # Clean description
                    if product.description:
                        original_desc = product.description
                        cleaned_desc = re.sub(r'\b[Gg]lantix\b', '', original_desc)
                        cleaned_desc = re.sub(r'\s*\|\s*\d{3,4}\s*\d{3,7}', '', cleaned_desc)
                        cleaned_desc = cleaned_desc.strip()
                        
                        if cleaned_desc != original_desc:
                            product.description = cleaned_desc
                            product.short_description = cleaned_desc[:255] if cleaned_desc else ''
                            desc_updated = True
                    
                    if name_updated or desc_updated:
                        product.save()
                        updated_count += 1
                        if updated_count % 100 == 0:
                            self.stdout.write(f'Cleaned {updated_count} products...')
                    else:
                        skipped_count += 1
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating product {product.slug}: {str(e)}'))
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f'\nGlantix reference removal complete:'))
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
