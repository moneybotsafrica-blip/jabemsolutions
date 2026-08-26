from django.db import migrations


def update_quote_contact_email(apps, schema_editor):
    QuoteSettings = apps.get_model("catalog", "QuoteSettings")
    QuoteSettings.objects.filter(email="jabemsolutionsltd@gmail.com").update(email="info@jabemsolutions.co.ke")
    QuoteSettings.objects.filter(terms__contains="jabemsolutionsltd@gmail.com").update(
        terms="""1. Payment: 100% before Dispatch.
2. Price Validity: Prices are valid for 14 days from the quotation date.
3. Delivery: On receipt of LPO / PAYMENT.
4. Warranty: One (1) Year Warranty where applicable from the date of installation.
5. The equipment should be plugged into a clean power source (UPS and adequate Earthing).
6. All goods remain the property of Jabem Solutions Limited until payment is received in full. Lipa Na Mpesa Paybill No-247247 Account Number: 309061 or Paybill-516600 Account Number: 309061. Business Name: Jabem Solutions Limited.

For Clarifications, please contact Jabem Solutions Limited, +254736 794 594, info@jabemsolutions.co.ke.
IMPORTANT - When making a payment, kindly pay against the Account above."""
    )


class Migration(migrations.Migration):
    dependencies = [("catalog", "0014_quoteitem_manual_label")]
    operations = [migrations.RunPython(update_quote_contact_email, migrations.RunPython.noop)]
