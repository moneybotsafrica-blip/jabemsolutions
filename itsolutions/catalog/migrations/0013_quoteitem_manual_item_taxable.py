from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("catalog", "0012_alter_quote_status")]
    operations = [
        migrations.AddField(model_name="quoteitem", name="item_name", field=models.CharField(blank=True, max_length=255, verbose_name="Manual item")),
        migrations.AddField(model_name="quoteitem", name="taxable", field=models.BooleanField(default=False, verbose_name="Apply VAT")),
    ]
