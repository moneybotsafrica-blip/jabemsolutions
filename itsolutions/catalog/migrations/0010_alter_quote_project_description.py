from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0009_quotes")]

    operations = [
        migrations.AlterField(
            model_name="quote",
            name="project_description",
            field=models.TextField(blank=True, verbose_name="Terms"),
        ),
    ]
