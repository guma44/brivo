# Generated by Django 3.0.12 on 2021-07-06 05:19

import brivo.brewery.fields
import brivo.utils.measures
from django.db import migrations, models
import django.db.models.deletion
import measurement.measures.temperature
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('brewery', '0003_auto_20210602_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='FermentationCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, editable=False, max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modified At')),
                ('gravity', brivo.brewery.fields.BeerGravityField(measurement=brivo.utils.measures.BeerGravity, null=True, verbose_name='Gravity')),
                ('temperature', brivo.brewery.fields.TemperatureField(measurement=measurement.measures.temperature.Temperature, null=True, verbose_name='Temperature')),
                ('sample_day', models.DateField(null=True, verbose_name='Sample Day')),
                ('batch', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='fermentation_checks', to='brewery.Batch', verbose_name='Batch')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
