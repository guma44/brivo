# Generated by Django 3.0.12 on 2021-02-26 12:57

import brivo.utils.measures
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_measurement.models
import measurement.measures.mass
import measurement.measures.temperature
import measurement.measures.volume


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('type', models.CharField(choices=[('ANY', 'Any'), ('SPICE', 'Spice'), ('FLAVOR', 'Flavor'), ('FINING', 'Fining'), ('HERB', 'Herb'), ('WATER AGENT', 'Water agent'), ('OTHER', 'Other')], max_length=255, verbose_name='Type')),
                ('use', models.CharField(choices=[('BOIL', 'Boil'), ('MASH', 'Mash'), ('PRIMARY', 'Primary'), ('SECONDARY', 'Secondary'), ('KEGING', 'Keging'), ('BOTTLING', 'Bottling'), ('OTHER', 'Other')], max_length=255, verbose_name='Use')),
            ],
        ),
        migrations.CreateModel(
            name='BaseFermentable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('type', models.CharField(choices=[('ADJUNCT', 'Adjunct'), ('GRAIN', 'Grain'), ('DRY EXTRACT', 'Dry extract'), ('LIQUID EXTRACT', 'Liquid extract'), ('SUGAR', 'Sugar')], max_length=255, verbose_name='Type')),
                ('color', django_measurement.models.MeasurementField(measurement=brivo.utils.measures.BeerColor, verbose_name='Color')),
                ('extraction', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Extraction')),
            ],
        ),
        migrations.CreateModel(
            name='BaseHop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('alpha_acids', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Alpha Acids')),
            ],
        ),
        migrations.CreateModel(
            name='BaseYeast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('lab', models.CharField(max_length=255, verbose_name='Lab')),
                ('type', models.CharField(choices=[('ALE', 'Ale'), ('LAGER', 'Lager'), ('WHEAT', 'Wheat'), ('WILD', 'Wild'), ('CHAMPAGNE', 'Champagne'), ('BACTERIA', 'Bacteria'), ('MIX', 'Mix')], max_length=255, verbose_name='Type')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
            ],
        ),
        migrations.CreateModel(
            name='Fermentation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_fermentation_temperature', django_measurement.models.MeasurementField(default=17, measurement=measurement.measures.temperature.Temperature, verbose_name='Primary Ferementation Temperature')),
                ('secondary_fermentation_temperature', django_measurement.models.MeasurementField(default=20, measurement=measurement.measures.temperature.Temperature, verbose_name='Secondary Fermentation Temperature')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Extra',
            fields=[
                ('baseextra_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseExtra')),
                ('desc', models.CharField(max_length=255, verbose_name='Description')),
                ('active', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Active')),
            ],
            bases=('brew.baseextra',),
        ),
        migrations.CreateModel(
            name='InventoryExtra',
            fields=[
                ('baseextra_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseExtra')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('comment', models.TextField(verbose_name='Comment')),
            ],
            bases=('brew.baseextra',),
        ),
        migrations.CreateModel(
            name='InventoryFermentable',
            fields=[
                ('basefermentable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseFermentable')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('comment', models.TextField(verbose_name='Comment')),
            ],
            bases=('brew.basefermentable',),
        ),
        migrations.CreateModel(
            name='InventoryHop',
            fields=[
                ('basehop_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseHop')),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Year')),
                ('form', models.CharField(choices=[('HOP PELLETS', 'Hop pellets'), ('WHOLE HOPS', 'Whole hops'), ('EXTRACT', 'Extract')], max_length=255, verbose_name='Form')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('comment', models.TextField(verbose_name='Comment')),
            ],
            bases=('brew.basehop',),
        ),
        migrations.CreateModel(
            name='InventoryYeast',
            fields=[
                ('baseyeast_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseYeast')),
                ('expiration_date', models.DateField(verbose_name='Expiration Date')),
                ('collected_at', models.DateField(blank=True, verbose_name='Collected At')),
                ('generation', models.CharField(blank=True, max_length=50, verbose_name='Generation')),
                ('form', models.CharField(choices=[('DRY', 'Dry'), ('LIQUID', 'Liquid'), ('SLURRY', 'Slurry'), ('CULTURE', 'Culture')], max_length=255, verbose_name='Form')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('comment', models.TextField(verbose_name='Comment')),
            ],
            bases=('brew.baseyeast',),
        ),
        migrations.CreateModel(
            name='Yeast',
            fields=[
                ('baseyeast_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseYeast')),
                ('lab_id', models.CharField(max_length=255, verbose_name='Lab ID')),
                ('atten_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Min Attenuation')),
                ('atten_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Max Attenuation')),
                ('flocc', models.CharField(max_length=255, verbose_name='Flocculation')),
                ('form', models.CharField(choices=[('DRY', 'Dry'), ('LIQUID', 'Liquid'), ('SLURRY', 'Slurry'), ('CULTURE', 'Culture')], max_length=255, verbose_name='Form')),
                ('temp_min', django_measurement.models.MeasurementField(measurement=measurement.measures.temperature.Temperature, verbose_name='Min Temperature')),
                ('temp_max', django_measurement.models.MeasurementField(measurement=measurement.measures.temperature.Temperature, verbose_name='Max Temperature')),
                ('alco_toler', models.CharField(max_length=255, verbose_name='Alcohol Tolerance')),
                ('styles', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Styles')),
                ('desc', models.CharField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('external_link', models.URLField(blank=True, max_length=255, null=True, verbose_name='External Link')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            bases=('brew.baseyeast',),
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.CharField(max_length=255, verbose_name='Catetory ID')),
                ('category', models.CharField(max_length=255, verbose_name='Category')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('og_min', django_measurement.models.MeasurementField(blank=True, measurement=brivo.utils.measures.BeerGravity, null=True, verbose_name='OG Max')),
                ('og_max', django_measurement.models.MeasurementField(blank=True, measurement=brivo.utils.measures.BeerGravity, null=True, verbose_name='OG Min')),
                ('fg_min', django_measurement.models.MeasurementField(blank=True, measurement=brivo.utils.measures.BeerGravity, null=True, verbose_name='FG Max')),
                ('fg_max', django_measurement.models.MeasurementField(blank=True, measurement=brivo.utils.measures.BeerGravity, null=True, verbose_name='FG Min')),
                ('ibu_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='IBU Max')),
                ('ibu_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='IBU Min')),
                ('color_min', django_measurement.models.MeasurementField(blank=True, measurement=brivo.utils.measures.BeerColor, null=True, verbose_name='Color Min')),
                ('color_max', django_measurement.models.MeasurementField(blank=True, measurement=brivo.utils.measures.BeerColor, null=True, verbose_name='Color Max')),
                ('alcohol_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Alcohol Min')),
                ('alcohol_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Alcohol Max')),
                ('ferm_type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Fermentation Type')),
                ('desc_aroma', models.TextField(blank=True, max_length=255, null=True, verbose_name='Aroma')),
                ('desc_appe', models.TextField(blank=True, max_length=255, null=True, verbose_name='Appearance')),
                ('desc_flavor', models.TextField(blank=True, max_length=255, null=True, verbose_name='Flavour')),
                ('desc_mouth', models.TextField(blank=True, max_length=255, null=True, verbose_name='Mouthfeel')),
                ('desc_overall', models.TextField(blank=True, max_length=255, null=True, verbose_name='Overall')),
                ('desc_comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('desc_history', models.TextField(blank=True, max_length=255, null=True, verbose_name='History')),
                ('desc_ingre', models.TextField(blank=True, max_length=255, null=True, verbose_name='Ingredients')),
                ('desc_style_comp', models.TextField(blank=True, max_length=255, null=True, verbose_name='Style Comparison')),
                ('commercial_exam', models.TextField(blank=True, max_length=255, null=True, verbose_name='Examples')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('tags', models.ManyToManyField(to='brew.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('ALL GRAIN', 'All Grain'), ('EXTRACT', 'Extract'), ('PARTIAL_MASH', 'Partial Mash')], max_length=255, verbose_name='Type')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('expected_beer_volume', django_measurement.models.MeasurementField(measurement=measurement.measures.volume.Volume, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Batch Volume')),
                ('boil_time', models.IntegerField(default=60.0, verbose_name='Boil Time')),
                ('evaporation_rate', models.DecimalField(decimal_places=2, default=10.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Evaporation Rate')),
                ('boil_loss', models.DecimalField(decimal_places=2, default=10.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Boil Loss')),
                ('trub_loss', models.DecimalField(decimal_places=2, default=5.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Trub Loss')),
                ('dry_hopping_loss', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Dry Hopping Loss')),
                ('mash_efficiency', models.DecimalField(decimal_places=2, default=75.0, max_digits=5, verbose_name='Mash Efficiency')),
                ('liquor_to_grist_ratio', models.DecimalField(decimal_places=2, default=3.0, max_digits=5, verbose_name='Liquor-To-Grist Ratio')),
                ('note', models.TextField(blank=True, max_length=255, verbose_name='Note')),
                ('is_public', models.BooleanField(default=True, verbose_name='Public')),
                ('style', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='brew.Style', verbose_name='Style')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='MashStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', django_measurement.models.MeasurementField(measurement=measurement.measures.temperature.Temperature, verbose_name='Temperature')),
                ('time', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Time')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mash_steps', to='brew.Recipe', verbose_name='Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(choices=[('MASHING', 'Mashing'), ('BOIL', 'Boil'), ('PRIMARY FERMENTATION', 'Primary Fermentation'), ('SECONDARY FERMENTATION', 'Secondary Fermentation'), ('PACKAGING', 'Packaging'), ('FINISHED', 'Finished')], default='MASHING', max_length=50, verbose_name='Stage')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('batch_number', models.IntegerField(verbose_name='Batch Number')),
                ('brewing_day', models.DateField(verbose_name='Brewing Day')),
                ('grain_temperature', django_measurement.models.MeasurementField(measurement=measurement.measures.temperature.Temperature, verbose_name='Grain Temperature')),
                ('sparging_temperature', django_measurement.models.MeasurementField(measurement=measurement.measures.temperature.Temperature, verbose_name='Sparging Temperature')),
                ('gravity_before_boil', django_measurement.models.MeasurementField(measurement=brivo.utils.measures.BeerGravity, verbose_name='Gravity Before Boil')),
                ('initial_gravity', django_measurement.models.MeasurementField(measurement=brivo.utils.measures.BeerGravity, verbose_name='Initial Gravity')),
                ('wort_volume', django_measurement.models.MeasurementField(measurement=measurement.measures.volume.Volume, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Wort Volume')),
                ('boil_waists', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Boil Waists')),
                ('primary_fermentation_start_day', models.DateField(verbose_name='Primary Fermentation Start Day')),
                ('secondary_fermentation_start_day', models.DateField(verbose_name='Secondary Fermentation Start Day')),
                ('post_primary_fermentation', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Post-primary Gravity')),
                ('packaging_date', models.DateField(verbose_name='Packaging Start Day')),
                ('end_gravity', django_measurement.models.MeasurementField(measurement=brivo.utils.measures.BeerGravity, verbose_name='End Gravity')),
                ('beer_volume', django_measurement.models.MeasurementField(measurement=measurement.measures.volume.Volume, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Beer Volume')),
                ('carbonation_type', models.CharField(choices=[('FORCED', 'forced'), ('REFERMENTATION', 'refermentation')], max_length=50, verbose_name='Carbonation Type')),
                ('carbonation_level', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Carbonation Level')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brew.Recipe', verbose_name='Recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='YeastIngredient',
            fields=[
                ('baseyeast_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseYeast')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('attenuation', models.DecimalField(blank=True, decimal_places=2, default=75.0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Attenuation')),
                ('form', models.CharField(choices=[('DRY', 'Dry'), ('LIQUID', 'Liquid'), ('SLURRY', 'Slurry'), ('CULTURE', 'Culture')], max_length=255, verbose_name='Form')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yeasts', to='brew.Recipe', verbose_name='Recipe')),
            ],
            bases=('brew.baseyeast',),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('inventory_extra', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brew.InventoryExtra', verbose_name='Extra')),
                ('inventory_fermentable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brew.InventoryFermentable', verbose_name='Fermentable')),
                ('inventory_hop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brew.InventoryHop', verbose_name='Hop')),
                ('inventory_yeast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brew.InventoryYeast', verbose_name='Yeast')),
            ],
        ),
        migrations.CreateModel(
            name='HopIngredient',
            fields=[
                ('basehop_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseHop')),
                ('use', models.CharField(choices=[('BOIL', 'Boil'), ('DRY HOP', 'Dry hop'), ('MASH', 'Mash'), ('AROMA', 'Aroma'), ('FIRST WORT', 'First wort'), ('WHIRPOOL', 'Whirpool')], max_length=255, verbose_name='Use')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('time', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Time')),
                ('time_unit', models.CharField(choices=[('MINUTE', 'minute'), ('HOUR', 'hour'), ('DAY', 'day'), ('WEEK', 'week'), ('MONTH', 'month'), ('YEAR', 'year')], max_length=255, verbose_name='Time Unit')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hops', to='brew.Recipe', verbose_name='Recipe')),
            ],
            bases=('brew.basehop',),
        ),
        migrations.CreateModel(
            name='Hop',
            fields=[
                ('basehop_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseHop')),
                ('external_link', models.URLField(blank=True, max_length=255, null=True, verbose_name='External Link')),
                ('alpha_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Alpha Min')),
                ('alpha_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Alpha Max')),
                ('beta_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Beta Min')),
                ('beta_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Beta Max')),
                ('co_humulone_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Co-Humulone Min')),
                ('co_humulone_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Co-Humulone Max')),
                ('total_oil_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Total Oil Min')),
                ('total_oil_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Total Oil Max')),
                ('myrcene_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Myrcene Min')),
                ('myrcene_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Myrcene Max')),
                ('humulene_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Humulene Min')),
                ('humulene_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Humulene Max')),
                ('caryophyllene_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Caryophyllene Min')),
                ('caryophyllene_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Caryophyllene Max')),
                ('farnesene_min', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Farnesene Min')),
                ('farnesene_max', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Farnesene Max')),
                ('type', models.CharField(choices=[('DUAL PURPOSE', 'Dual Purpose'), ('AROMA', 'Aroma'), ('BITTERING', 'Bittering')], max_length=50, verbose_name='Type')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='brew.Country', verbose_name='Country')),
                ('substitute', models.ManyToManyField(blank=True, null=True, to='brew.Hop', verbose_name='Substitue')),
            ],
            bases=('brew.basehop',),
        ),
        migrations.CreateModel(
            name='FermentableIngredient',
            fields=[
                ('basefermentable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseFermentable')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('use', models.CharField(choices=[('MASHING', 'Mashing'), ('BOIL', 'Boil'), ('LATE BOIL', 'Late boil'), ('STEEP', 'Steep')], max_length=255, verbose_name='Fermentable Use')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fermentables', to='brew.Recipe', verbose_name='Recipe')),
            ],
            bases=('brew.basefermentable',),
        ),
        migrations.CreateModel(
            name='Fermentable',
            fields=[
                ('basefermentable_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseFermentable')),
                ('max_use', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Max Use')),
                ('description', models.TextField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('external_link', models.URLField(blank=True, max_length=255, null=True, verbose_name='External Link')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='brew.Country', verbose_name='Country')),
            ],
            bases=('brew.basefermentable',),
        ),
        migrations.CreateModel(
            name='ExtraIngredient',
            fields=[
                ('baseextra_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='brew.BaseExtra')),
                ('amount', django_measurement.models.MeasurementField(measurement=measurement.measures.mass.Mass, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('time', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Time')),
                ('time_unit', models.CharField(choices=[('MINUTE', 'minute'), ('HOUR', 'hour'), ('DAY', 'day'), ('WEEK', 'week'), ('MONTH', 'month'), ('YEAR', 'year')], max_length=255, verbose_name='Time Unit')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extras', to='brew.Recipe', verbose_name='Recipe')),
            ],
            bases=('brew.baseextra',),
        ),
    ]
