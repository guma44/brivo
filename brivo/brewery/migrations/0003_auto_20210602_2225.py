# Generated by Django 3.0.12 on 2021-06-02 20:25

import brivo.brewery.fields
from django.db import migrations, models
import measurement.measures.temperature


class Migration(migrations.Migration):

    dependencies = [
        ('brewery', '0002_auto_20210516_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='priming_temperature',
            field=brivo.brewery.fields.TemperatureField(blank=True, measurement=measurement.measures.temperature.Temperature, null=True, verbose_name='Priming Temperature'),
        ),
        migrations.AddField(
            model_name='batch',
            name='sugar_type',
            field=models.CharField(blank=True, choices=[('CORN_SUGAR', 'Corn Sugar'), ('TABLE_SUGAR', 'Table Sugar'), ('DRY_EXTRACT', 'Dry Extract')], max_length=50, null=True, verbose_name='Sugar Type'),
        ),
    ]