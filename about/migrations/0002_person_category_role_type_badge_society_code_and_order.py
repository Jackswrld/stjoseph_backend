from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("about", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="category",
            field=models.CharField(
                choices=[
                    ("clergy", "Clergy"),
                    ("official", "Official"),
                    ("society_leader", "Society leader"),
                ],
                default="official",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="person",
            name="role_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("parish_priest", "Parish priest"),
                    ("assistant_priest", "Assistant priest"),
                    ("catechist", "Catechist"),
                ],
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="badge",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="person",
            name="society_code",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterModelOptions(
            name="person",
            options={
                "ordering": ["display_order", "id"],
                "verbose_name_plural": "people",
            },
        ),
    ]
