import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import unquote, urlparse

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from catalog.models import Product


class Command(BaseCommand):
    help = "Upload local media files to Cloudinary while preserving their paths."

    def add_arguments(self, parser):
        parser.add_argument("--workers", type=int, default=8)
        parser.add_argument("--database-products-only", action="store_true")

    def handle(self, *args, **options):
        cloudinary_url = urlparse(os.environ.get("CLOUDINARY_URL", ""))
        cloud_name = cloudinary_url.hostname
        api_key = cloudinary_url.username
        api_secret = unquote(cloudinary_url.password or "")

        if not all((cloud_name, api_key, api_secret)):
            raise CommandError("Set CLOUDINARY_URL before running this command.")

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        media_root = Path(settings.MEDIA_ROOT)
        products_by_image = {}
        if options["database_products_only"]:
            products_by_image = {
                product.image.name: product
                for product in Product.objects.exclude(image="")
                if product.image and product.image.name
            }
            media_files = [
                media_root / image_name
                for image_name in products_by_image
                if (media_root / image_name).is_file()
            ]
        else:
            media_files = [path for path in media_root.rglob("*") if path.is_file()]
        def upload_image(image_path):
            relative_path = image_path.relative_to(media_root)
            public_id = (Path("jabem-media") / relative_path).as_posix()
            try:
                result = cloudinary.uploader.upload(
                    str(image_path),
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image",
                )
                return relative_path, result["secure_url"], None
            except Exception as error:
                return relative_path, None, error

        uploaded = 0
        failed = 0
        products_to_update = []
        with ThreadPoolExecutor(max_workers=options["workers"]) as executor:
            futures = [executor.submit(upload_image, image_path) for image_path in media_files]
            for future in as_completed(futures):
                relative_path, secure_url, error = future.result()
                if error:
                    failed += 1
                    self.stderr.write(f"Failed {relative_path}: {error}")
                else:
                    uploaded += 1
                    product = products_by_image.get(relative_path.as_posix())
                    if product and product.external_image_url != secure_url:
                        product.external_image_url = secure_url
                        products_to_update.append(product)
                    if uploaded % 100 == 0:
                        self.stdout.write(f"Uploaded {uploaded}/{len(media_files)} files")

        if products_to_update:
            Product.objects.bulk_update(products_to_update, ["external_image_url"])
            self.stdout.write(f"Updated {len(products_to_update)} product image URLs.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Cloudinary sync complete: {uploaded} uploaded, {failed} failed."
            )
        )
