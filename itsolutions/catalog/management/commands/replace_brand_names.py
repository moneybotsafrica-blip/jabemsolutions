from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Product


class Command(BaseCommand):
    help = 'Replace mustek and glantix with jabem in product descriptions'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Replace mustek variants
            mustek_products = Product.objects.filter(description__icontains='mustek')
            mustek_count = mustek_products.count()
            
            for product in mustek_products:
                product.description = product.description.replace('mustek', 'jabem').replace('Mustek', 'Jabem').replace('MUSTEK', 'JABEM')
                product.short_description = product.short_description.replace('mustek', 'jabem').replace('Mustek', 'Jabem').replace('MUSTEK', 'JABEM')
                product.save()
            
            # Replace glantix variants
            glantix_products = Product.objects.filter(description__icontains='glantix')
            glantix_count = glantix_products.count()
            
            for product in glantix_products:
                product.description = product.description.replace('glantix', 'jabem').replace('Glantix', 'Jabem').replace('GLANTIX', 'JABEM')
                product.short_description = product.short_description.replace('glantix', 'jabem').replace('Glantix', 'Jabem').replace('GLANTIX', 'JABEM')
                product.save()
            
            self.stdout.write(self.style.SUCCESS(f'Updated {mustek_count} products with mustek references'))
            self.stdout.write(self.style.SUCCESS(f'Updated {glantix_count} products with glantix references'))
            self.stdout.write(self.style.SUCCESS(f'Total updated: {mustek_count + glantix_count} products'))
