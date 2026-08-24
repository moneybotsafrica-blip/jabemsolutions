import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Product

# Set UTF-8 encoding for stdout to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class Command(BaseCommand):
    help = 'Generate product descriptions from product names and categories'

    def handle(self, *args, **options):
        updated_count = 0
        skipped_count = 0

        for product in Product.objects.all():
            try:
                if not product.description or product.description.strip() == '':
                    description = self.generate_description(product)
                    product.description = description
                    product.short_description = description[:255]
                    product.save()
                    updated_count += 1
                    if updated_count % 100 == 0:
                        self.stdout.write(f'Generated descriptions for {updated_count} products...')
                else:
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating product {product.slug}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nDescription generation complete:'))
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Skipped (already had descriptions): {skipped_count}')

    def generate_description(self, product):
        """Generate a description based on product name and category"""
        name = product.name.lower()
        category = product.category.name.lower() if product.category else ''
        
        # Extract key information from product name
        description_parts = []
        
        # Add category-specific descriptions
        if 'laptop' in name or 'notebook' in name:
            if 'gaming' in name:
                description_parts.append("High-performance gaming laptop designed for immersive gaming experiences.")
            elif 'business' in name or 'professional' in name:
                description_parts.append("Professional laptop designed for business productivity and reliability.")
            else:
                description_parts.append("Versatile laptop perfect for work, entertainment, and everyday computing.")
            
            # Add specs hints if present
            if 'core i' in name or 'ryzen' in name or 'm1' in name or 'm2' in name or 'm3' in name:
                description_parts.append("Features powerful processor for smooth multitasking.")
            if '16gb' in name or '32gb' in name:
                description_parts.append("High RAM capacity for demanding applications.")
            if '512gb' in name or '1tb' in name or '2tb' in name:
                description_parts.append("Ample storage for all your files and applications.")
                
        elif 'desktop' in name or 'tower' in name or 'pc' in name:
            description_parts.append("Powerful desktop computer for demanding computing tasks.")
            
        elif 'monitor' in name:
            description_parts.append("High-quality display delivering crisp and vibrant visuals.")
            if '4k' in name or 'uhd' in name:
                description_parts.append("Ultra HD resolution for stunning clarity.")
                
        elif 'printer' in name:
            description_parts.append("Reliable printing solution for home or office use.")
            if 'laser' in name:
                description_parts.append("Laser technology for sharp, professional documents.")
            elif 'inkjet' in name:
                description_parts.append("Inkjet technology for vibrant color printing.")
                
        elif 'router' in name or 'switch' in name:
            description_parts.append("Networking equipment for reliable connectivity.")
            if 'wifi' in name or 'wireless' in name:
                description_parts.append("Wireless capability for flexible network setup.")
                
        elif 'camera' in name:
            if 'cctv' in name or 'security' in name:
                description_parts.append("Security camera for surveillance and monitoring.")
            else:
                description_parts.append("High-quality camera for capturing moments.")
                
        elif 'ram' in name or 'memory' in name:
            description_parts.append("Memory module for upgrading system performance.")
            
        elif 'ssd' in name or 'hard drive' in name or 'hdd' in name:
            description_parts.append("Storage solution for fast data access and ample space.")
            
        elif 'battery' in name:
            description_parts.append("Replacement battery for extended device runtime.")
            
        elif 'charger' in name or 'adapter' in name:
            description_parts.append("Power adapter for reliable device charging.")
            
        elif 'keyboard' in name:
            description_parts.append("Keyboard for comfortable and efficient typing.")
            
        elif 'mouse' in name:
            description_parts.append("Mouse for precise cursor control and navigation.")
            
        elif 'headset' in name or 'headphone' in name:
            description_parts.append("Audio headset for clear communication and entertainment.")
            
        elif 'speaker' in name:
            description_parts.append("Speaker system for high-quality audio output.")
            
        elif 'projector' in name:
            description_parts.append("Projector for displaying presentations and media on large screens.")
            
        elif 'ups' in name or 'power' in name:
            description_parts.append("Power protection equipment for uninterrupted operation.")
            
        elif 'cable' in name or 'cord' in name:
            description_parts.append("Connectivity cable for reliable data and power transfer.")
            
        elif 'toner' in name or 'ink' in name or 'cartridge' in name:
            description_parts.append("Printing consumable for high-quality document output.")
            
        elif 'software' in category or 'license' in name:
            description_parts.append("Software license for authorized use of the application.")
            
        elif 'pos' in category or 'point of sale' in category:
            description_parts.append("Point of sale equipment for efficient business transactions.")
            
        else:
            # Generic description based on category
            if 'hardware' in category:
                description_parts.append("Quality hardware component for your computing needs.")
            elif 'software' in category:
                description_parts.append("Software solution for enhanced productivity.")
            elif 'service' in category:
                description_parts.append("Professional service to support your business needs.")
            else:
                description_parts.append("Quality product designed to meet your needs.")
        
        # Add brand information if available
        if product.brand:
            description_parts.append(f"Manufactured by {product.brand.name}, a trusted brand in the industry.")
        
        # Combine parts into a coherent description
        if description_parts:
            description = ' '.join(description_parts)
            # Capitalize first letter
            description = description[0].upper() + description[1:]
            return description
        else:
            # Fallback to a simple description
            return f"{product.name} - Quality product from {product.category.name if product.category else 'our catalog'}."
