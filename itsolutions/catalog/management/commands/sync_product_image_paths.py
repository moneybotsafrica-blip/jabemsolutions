import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from catalog.models import Product


class Command(BaseCommand):
    help = "Sync product image paths from the local product fixture into the database."

    def handle(self, *args, **options):
        fixture_path = Path(settings.BASE_DIR).parent / "local_data.json"
        with fixture_path.open(encoding="utf-8") as fixture_file:
            fixture_data = json.load(fixture_file)

        image_paths = {
            item["fields"]["sku"]: item["fields"].get("image", "")
            for item in fixture_data
            if item.get("model") == "catalog.product" and item["fields"].get("image")
        }
        products_by_sku = Product.objects.in_bulk(image_paths, field_name="sku")
        products_to_update = []

        for sku, image_path in image_paths.items():
            product = products_by_sku.get(sku)
            if product and product.image.name != image_path:
                product.image.name = image_path
                products_to_update.append(product)

        Product.objects.bulk_update(products_to_update, ["image"])
        self.stdout.write(
            self.style.SUCCESS(
                f"Synced image paths for {len(products_to_update)} products."
            )
        )
