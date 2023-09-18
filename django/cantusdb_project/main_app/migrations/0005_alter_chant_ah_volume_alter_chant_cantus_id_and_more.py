# Generated by Django 4.2.3 on 2023-09-14 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0004_alter_chant_source_alter_sequence_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chant",
            name="ah_volume",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="AH volume"
            ),
        ),
        migrations.AlterField(
            model_name="chant",
            name="cantus_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                verbose_name="cantus ID",
            ),
        ),
        migrations.AlterField(
            model_name="chant",
            name="cao_concordances",
            field=models.CharField(
                blank=True, max_length=63, null=True, verbose_name="CAO concordances"
            ),
        ),
        migrations.AlterField(
            model_name="chant",
            name="differentia_new",
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                verbose_name="differentiae database",
            ),
        ),
        migrations.AlterField(
            model_name="sequence",
            name="ah_volume",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="AH volume"
            ),
        ),
        migrations.AlterField(
            model_name="sequence",
            name="cantus_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=255,
                null=True,
                verbose_name="cantus ID",
            ),
        ),
        migrations.AlterField(
            model_name="sequence",
            name="cao_concordances",
            field=models.CharField(
                blank=True, max_length=63, null=True, verbose_name="CAO concordances"
            ),
        ),
        migrations.AlterField(
            model_name="sequence",
            name="differentia_new",
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                verbose_name="differentiae database",
            ),
        ),
    ]
