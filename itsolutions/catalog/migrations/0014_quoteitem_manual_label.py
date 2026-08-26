from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("catalog", "0013_quoteitem_manual_item_taxable")]
    operations = [
        migrations.AlterField(
            model_name="quoteitem",
            name="item_name",
            field=models.CharField(max_length=255, blank=True, verbose_name="Product (manual item)"),
        ),
    ]
