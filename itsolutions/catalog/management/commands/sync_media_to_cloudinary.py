import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import unquote, urlparse

import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Upload local media files to Cloudinary while preserving their paths."

    def add_arguments(self, parser):
        parser.add_argument("--workers", type=int, default=8)

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
        media_files = [path for path in media_root.rglob("*") if path.is_file()]
        def upload_image(image_path):
            relative_path = image_path.relative_to(media_root)
            public_id = (Path("jabem-media") / relative_path).with_suffix("").as_posix()
            try:
                cloudinary.uploader.upload(
                    str(image_path),
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image",
                )
                return relative_path, None
            except Exception as error:
                return relative_path, error

        uploaded = 0
        failed = 0
        with ThreadPoolExecutor(max_workers=options["workers"]) as executor:
            futures = [executor.submit(upload_image, image_path) for image_path in media_files]
            for future in as_completed(futures):
                relative_path, error = future.result()
                if error:
                    failed += 1
                    self.stderr.write(f"Failed {relative_path}: {error}")
                else:
                    uploaded += 1
                    if uploaded % 100 == 0:
                        self.stdout.write(f"Uploaded {uploaded}/{len(media_files)} files")

        self.stdout.write(
            self.style.SUCCESS(
                f"Cloudinary sync complete: {uploaded} uploaded, {failed} failed."
            )
        )
