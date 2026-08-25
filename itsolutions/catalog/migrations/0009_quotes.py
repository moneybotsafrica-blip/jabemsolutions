from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def default_valid_until():
    return date.today() + timedelta(days=30)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0008_alter_product_product_type"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QuoteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("company_name", models.CharField(default="Jabem Solutions Ltd", max_length=160)),
                ("logo_url", models.URLField(blank=True, help_text="Optional public logo URL. The site logo is used when blank.", max_length=500)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.TextField(blank=True)),
                ("business_number", models.CharField(blank=True, max_length=100, verbose_name="Business / tax number")),
                ("bank_details", models.TextField(blank=True)),
                ("payment_details", models.TextField(default="Payment is due before delivery or installation.")),
                ("terms", models.TextField(default="Please confirm acceptance of this quote before work begins. Prices are valid for the period shown above.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Quote settings", "verbose_name_plural": "Quote settings"},
        ),
        migrations.CreateModel(
            name="Quote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quote_number", models.CharField(blank=True, editable=False, max_length=40, unique=True)),
                ("client_name", models.CharField(max_length=160)),
                ("client_company", models.CharField(blank=True, max_length=160)),
                ("client_phone", models.CharField(blank=True, max_length=40)),
                ("client_email", models.EmailField(blank=True, max_length=254)),
                ("client_address", models.TextField(blank=True)),
                ("project_description", models.TextField(blank=True)),
                ("issued_date", models.DateField(default=date.today)),
                ("valid_until", models.DateField(default=default_valid_until)),
                ("tax_rate", models.DecimalField(decimal_places=2, default=Decimal("16.00"), max_digits=5)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("sent", "Sent"), ("accepted", "Accepted"), ("expired", "Expired")], default="draft", max_length=12)),
                ("notes", models.TextField(blank=True, help_text="Optional notes shown above the standard terms.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="quotes_created", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="QuoteItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(blank=True, max_length=255)),
                ("unit_price", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("order", models.PositiveIntegerField(default=0)),
                ("product", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="catalog.product")),
                ("quote", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="catalog.quote")),
            ],
            options={"ordering": ["order", "pk"]},
        ),
    ]
