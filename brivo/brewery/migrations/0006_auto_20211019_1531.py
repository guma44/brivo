# Generated by Django 3.0.12 on 2021-10-19 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brewery', '0005_auto_20210707_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientextra',
            name='time',
            field=models.DecimalField(decimal_places=5, max_digits=10, verbose_name='Time'),
        ),
    ]