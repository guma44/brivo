# Generated by Django 3.0.12 on 2021-04-30 12:47

import brivo.utils.measures
import django.core.validators
from django.db import migrations, models
import django_measurement.models


class Migration(migrations.Migration):

    dependencies = [
        ('brew', '0002_auto_20210416_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basefermentable',
            name='color',
            field=django_measurement.models.MeasurementField(measurement=brivo.utils.measures.BeerColor, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='basefermentable',
            name='extraction',
            field=models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Extraction'),
        ),
        migrations.AlterField(
            model_name='basefermentable',
            name='type',
            field=models.CharField(choices=[('ADJUNCT', 'Adjunct'), ('GRAIN', 'Grain'), ('DRY EXTRACT', 'Dry extract'), ('LIQUID EXTRACT', 'Liquid extract'), ('SUGAR', 'Sugar')], max_length=1000, verbose_name='Type'),
        ),
    ]