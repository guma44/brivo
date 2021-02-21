from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_measurement.models import MeasurementField
from measurement.measures import Volume, Weight, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.utils import functions


FERMENTABLE_TYPE = (
    ('ADJUNCT', 'Adjunct'),
    ('BASE MALT', 'Base malt'),
    ('CRYSTAL MALT', 'Crystal malt'),
    ('DRY EXTRACT', 'Dry extract'),
    ('LIQUID EXTRACT', 'Liquid extract'),
    ('ROASTED MALT', 'Roasted malt'),
    ('SUGAR', 'Sugar')
)


BATCH_STAGES = (
    ("MASHING", "Mashing"),
    ("BOILING", "Boiling"),
    ("PRIMARY_FERMENTATION", "Primary Fermentation"),
    ("SECONDARY_FERMENTATION", "Secondary Fermentation"),
    ("PACKAGING", "Packaging"),
    ("FINISHED", "Finished")
)

BATCH_STAGE_ORDER = [bs[0] for bs in BATCH_STAGES]

CARBONATION_TYPE = (
    ("FORCED", "forced"),
    ("REFERMENTATION", "refermentation")
)


EXTRA_TYPE = [
    ('ANY', 'Any'),
    ('SPICE', 'Spice'),
    ('FLAVOR', 'Flavor'),
    ('FINING', 'Fining'),
    ('HERB', 'Herb'),
    ('WATER AGENT', 'Water agent'),
    ('OTHER', 'Other')
]

EXTRA_USE = [
    ('BOIL', 'Boil'),
    ('MASH', 'Mash'),
    ('PRIMARY', 'Primary'),
    ('SECONDARY', 'Secondary'),
    ('KEGING', 'Keging'),
    ('BOTTLING', 'Bottling'),
    ('OTHER', 'Other')
]


FERMENTABLE_USE = [('MASHING', 'Mashing'),
 ('BOILING', 'Boiling'),
 ('LATE BOILING', 'Late boiling'),
 ('STEEP', 'Steep')]


HOP_USE = [('BOILING', 'Boiling'),
 ('DRY HOP', 'Dry hop'),
 ('MASH', 'Mash'),
 ("AROMA", "Aroma"),
 ('FIRST WORT', 'First wort'),
 ('WHIRPOOL', 'Whirpool')]


HOP_FORM = [
    ('HOP PELLETS', 'Hop pellets'),
    ('WHOLE HOPS', 'Whole hops'),
    ('EXTRACT', 'Extract')
]


YEAST_TYPE = [
    ('ALE', 'Ale'),
    ('LAGER', 'Lager'),
    ('WILD', 'Wild'),
    ('CHAMPAGNE', 'Champagne'),
    ('BACTERIA', 'Bacteria'),
    ('MIX', 'Mix')
]


YEAST_FORM = [
    ('DRY', 'Dry'),
    ('LIQUID', 'Liquid'),
    ('SLURRY', 'Slurry'),
    ('CULTURE', 'Culture')
]

TIME_CHOICE = [('MINUTE', 'minute'),
 ('HOUR', 'hour'),
 ('DAY', 'day'),
 ('WEEK', 'week'),
 ('MONTH', 'month'),
 ('YEAR', 'year')
 ]


RECIPE_TYPE = [('GRAIN', 'Grain'),
 ('EXTRACT', 'Extract'),
 ('PARTIAL_MASH', 'Partial Mash')
]


class Tag(models.Model):
    name = models.CharField(_("Name"), max_length=255)

class BaseFermentable(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=FERMENTABLE_TYPE)
    color = MeasurementField(measurement=BeerColor, verbose_name=_("Color"))
    fermentable_yield = models.DecimalField(_("Yield"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])


class BaseHop(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    alpha_acids = models.DecimalField(_("Alpha Acids"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])


class BaseExtra(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=EXTRA_TYPE)


class BaseYeast(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    lab = models.CharField(_("Lab"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=YEAST_TYPE)

class BaseExtra(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    short_link = models.CharField(_("Short Link"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=EXTRA_TYPE)
    description = models.CharField(_("Description"), max_length=255)
    active = models.DecimalField(_("Active"), max_digits=5, decimal_places=2)


class Fermentable(BaseFermentable):
    max_use = models.DecimalField(_("Max Use"), max_digits=5, decimal_places=2)
    description = models.TextField(_("Description"), max_length=255)
    external_link = models.URLField(_("External Link"), max_length=255)
    comment = models.TextField(_("Comment"))
    active = models.BooleanField(_("Active"), default=True)


class Hop(BaseHop):
    external_link = models.URLField(_("External Link"), max_length=255)
    description = models.TextField(_("Description"), max_length=255)
    comment = models.TextField(_("Comment"))
    active = models.BooleanField(_("Active"), default=True)


class Yeast(BaseYeast):
    lab_id = models.CharField(_("Lab ID"), max_length=255)
    atten_min = models.DecimalField(_("Min Attenuation"), max_digits=5, decimal_places=2)
    atten_max = models.DecimalField(_("Max Attenuation"), max_digits=5, decimal_places=2)
    flocc = models.CharField(_("Flocculation"), max_length=255)
    temp_min = MeasurementField(measurement=Temperature, verbose_name=_("Min Temperature"))
    temp_max = MeasurementField(measurement=Temperature, verbose_name=_("Max Temperature"))
    alco_toler = models.CharField(_("Alcohol Tolerance"), max_length=255)
    styles = models.CharField(_("Styles"), max_length=255)
    description = models.CharField(_("Description"), max_length=255)
    external_link = models.URLField(_("External Link"), max_length=255)
    comment = models.TextField(_("Comment"))
    active = models.DecimalField(_("Active"), max_digits=5, decimal_places=2)


class Style(models.Model):
    category_id = models.CharField(_("Catetory ID"), max_length=255)
    category = models.CharField(_("Category"), max_length=255)
    name = models.CharField(_("Name"), max_length=255)
    og_min = models.DecimalField(_("OG Max"), max_digits=5, decimal_places=2)
    og_max = models.DecimalField(_("OG Min"), max_digits=5, decimal_places=2)
    fg_min = models.DecimalField(_("FG Max"), max_digits=5, decimal_places=2)
    fg_max = models.DecimalField(_("FG Min"), max_digits=5, decimal_places=2)
    ibu_min = models.DecimalField(_("IBU Max"), max_digits=5, decimal_places=2)
    ibu_max = models.DecimalField(_("IBU Min"), max_digits=5, decimal_places=2)
    color_min = MeasurementField(measurement=BeerColor, verbose_name=_("Color Min"))
    color_max = MeasurementField(measurement=BeerColor, verbose_name=_("Color Max"))
    alcohol_min = models.DecimalField(_("Alcohol Min"), max_digits=5, decimal_places=2)
    alcohol_max = models.DecimalField(_("Alcohol Max"), max_digits=5, decimal_places=2)
    ferm_type = models.CharField(_("Fermentation Type"), max_length=255)
    desc_aroma = models.TextField(_("Aroma"), max_length=255)
    desc_appe = models.TextField(_("Appearance"), max_length=255)
    desc_flavor = models.TextField(_("Flavour"), max_length=255)
    desc_mouth = models.TextField(_("Mouthfeel"), max_length=255)
    desc_overall = models.TextField(_("Overall"), max_length=255)
    desc_comment = models.TextField(_("Comment"))
    desc_history = models.TextField(_("History"), max_length=255)
    tags = models.ManyToManyField("brew.Tag")
    active = models.BooleanField(_("Active"), default=True)


# class Country(models.Model):
#     name = models.CharField(_("Name"), max_length=255)
#     code = models.CharField(_("Code"), max_length=255)

class InventoryFermentable(BaseFermentable):
    amount = MeasurementField(measurement=Weight, unit_choices=["g", "kg", "oz", "lb"], validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))

class InventoryHop(BaseHop):
    year = models.IntegerField(_("Year"), validators=[MinValueValidator(0)])
    form = models.CharField(_("Form"), max_length=255, choices=HOP_FORM)
    amount = MeasurementField(measurement=Weight, unit_choices=["g", "kg", "oz", "lb"], validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))


class InventoryYeast(BaseYeast):
    expiration_date = models.DateField(_("Expiration Date"), auto_now=False, auto_now_add=False)
    collected_at = models.DateField(_("Collected At"), auto_now=False, auto_now_add=False, blank=True)
    generation = models.CharField(_("Generation"), max_length=50, blank=True)
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)
    amount = MeasurementField(measurement=Weight, unit_choices=["g", "kg", "oz", "lb"], validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))

class InventoryExtra(BaseExtra):
    amount = MeasurementField(measurement=Weight, unit_choices=["g", "kg", "oz", "lb"], validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))


class Inventory(models.Model):
    user = models.OneToOneField("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    inventory_fermentable = models.ForeignKey("InventoryFermentable", verbose_name=_("Fermentable"), on_delete=models.CASCADE)
    inventory_yeast = models.ForeignKey("InventoryYeast", verbose_name=_("Yeast"), on_delete=models.CASCADE)
    inventory_hop = models.ForeignKey("InventoryHop", verbose_name=_("Hop"), on_delete=models.CASCADE)
    inventory_extra = models.ForeignKey("InventoryExtra", verbose_name=_("Extra"), on_delete=models.CASCADE)

class FermentableIngredient(BaseFermentable):
    amount = MeasurementField(measurement=Weight, unit_choices=["g", "kg", "oz", "lb"], validators=[MinValueValidator(0)])
    use = models.CharField(_("Fermentable Use"), max_length=255, choices=FERMENTABLE_USE)

class HopIngredient(BaseHop):
    use = models.CharField(_("Use"), max_length=255, choices=HOP_USE)
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)


class YeastIngredient(BaseYeast):
    amount = MeasurementField(measurement=Weight, unit_choices=["g", "kg", "oz", "lb"], validators=[MinValueValidator(0)]),
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)


class ExtraIngredient(BaseExtra):
    use = models.CharField(_("Use"), max_length=255, choices=EXTRA_USE)
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2)
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)


class Fermentation(models.Model):
    primary_fermentation_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Primary Ferementation Temperature"), default=17)
    secondary_fermentation_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Secondary Fermentation Temperature"), default=20)


class MashStep(models.Model):
    temperature = MeasurementField(measurement=Temperature, verbose_name=_("Temperature"))
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, default=0)
    note = models.TextField(_("Note"), blank=True)


class Recipe(models.Model):
    user = models.ForeignKey("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    # Recipe info
    type = models.CharField(_("Type"), max_length=255, choices=RECIPE_TYPE)
    name = models.CharField(_("Name"), max_length=255)
    style = models.ManyToManyField("Style", _("Style"))
    # Batch info
    batch_volume = MeasurementField(measurement=Volume, verbose_name=_("Batch Volume"), unit_choices=["l", "ml", "oz", "gal"], validators=[MinValueValidator(0)])
    boil_time = models.IntegerField(_("Boil Time"))
    evaporation_rate = models.DecimalField(_("Evaporation Rate"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    boil_loss = models.DecimalField(_("Boil Loss"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    turb_loss = models.DecimalField(_("Trub Loss"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    dry_hopping_loss = models.DecimalField(_("Dry Hopping Loss"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    # Ingredients
    fermentables = models.ForeignKey("FermentableIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    hops = models.ForeignKey("HopIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    yeasts = models.ForeignKey("YeastIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    extras = models.ForeignKey("ExtraIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    # Mashing
    mash_efficiency = models.DecimalField(_("Mash Efficiency"), max_digits=5, decimal_places=2, default=75)
    liquor_to_grist_ration = models.DecimalField(_("Liquor-To-Grist Ratio"), max_digits=5, decimal_places=2)
    mashing = models.ForeignKey("MashStep", verbose_name=_(""), on_delete=models.CASCADE)
    # Rest
    note = models.TextField(_("Note"), max_length=255, blank=True)
    is_public = models.BooleanField(_("Public"), default=True)

    def get_boil_size(self):
        pass

    def get_pre_boil_gravity(self):
        pass

    def get_primary_size(self):
        pass

    def get_secondary_size(self):
        pass

    def get_color(self):
        pass

    def get_abv(self):
        pass

    def get_gravity(self):
        pass

    def get_bitterness(self):
        pass

    def get_bitterness_ratio(self):
        pass

    def get_mash_size(self):
        pass

    def get_total_mash_volume(self):
        pass


class Batch(models.Model):
    # Operational fields
    stage = models.CharField(_("Stage"), max_length=50, choices=BATCH_STAGES, default="MASHING")
    recipe = models.ForeignKey("brew.Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    # Stage 1 fields: info and mashing
    name = models.CharField(_("Name"), max_length=255)
    batch_number = models.IntegerField(_("Batch Number"))
    brewing_day = models.DateField(_("Brewing Day"), auto_now=False, auto_now_add=False)
    grain_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Grain Temperature"))
    sparging_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Sparging Temperature"))

    # Stage 2 fields: boiling
    gravity_before_boil = MeasurementField(measurement=BeerGravity, verbose_name=_("Gravity Before Boil"))

    # Stage 3 fields: primary fermentation
    initial_gravity = MeasurementField(measurement=BeerGravity, verbose_name=_("Initial Gravity"))
    wort_volume = MeasurementField(measurement=Volume, verbose_name=_("Wort Volume"), unit_choices=["l", "ml", "oz", "gal"], validators=[MinValueValidator(0)])
    boil_waists = models.DecimalField(_("Boil Waists"), max_digits=5, decimal_places=2)
    primary_fermentation_start_day = models.DateField(_("Primary Fermentation Start Day"), auto_now=False, auto_now_add=False)

    # Stage 4 fields: secondary fermentation
    secondary_fermentation_start_day = models.DateField(_("Secondary Fermentation Start Day"), auto_now=False, auto_now_add=False)
    post_primary_fermentation = models.DecimalField(_("Post-primary Gravity"), max_digits=5, decimal_places=2)

    # Stage 4 fields: packaging
    packaging_date = models.DateField(_("Packaging Start Day"), auto_now=False, auto_now_add=False)
    end_gravity = MeasurementField(measurement=BeerGravity, verbose_name=_("End Gravity"))
    beer_volume = MeasurementField(measurement=Volume, verbose_name=_("Beer Volume"), unit_choices=["l", "ml", "oz", "gal"], validators=[MinValueValidator(0)])
    carbonation_type = models.CharField(_("Carbonation Type"), max_length=50, choices=CARBONATION_TYPE)
    carbonation_level = models.DecimalField(_("Carbonation Level"), max_digits=5, decimal_places=2)

    hidden_fields = ["stage"]
    required_fields = ["recipe",]

    def get_expected_gravity(self):
        pass

    def get_size_with_trub_loss(self):
        pass

    def get_estimated_boil_loss(self):
        pass

    def get_actuall_mash_efficiency(self):
        pass

    def get_batch_bitterness(self):
        pass

    def get_abv(self):
        pass

    def get_attenuation(self):
        pass

    def get_calories(self):
        pass

    @staticmethod
    def get_fields_by_stage(stage):
        fields = ["stage"]  # Must always be present
        if stage == "MASHING":
            fields.extend([
                "name",
                "batch_number",
                "brewing_dat",
                "grain_temperature",
                "sparging_temperature"])
        elif stage == "BOILING":
            fields.extend(["gravity_before_boil"])
        elif stage == "PRIMARY_FERMENTATION":
            fields.extend([
                "initial_gravity",
                "wort_volume",
                "boil_waists",
                "primary_fermentation_start_day"
            ])
        elif stage == "SECONDARY_FERMENTATION":
            fields.extend([
                "gravity_after_secondary_fermentation",
                "secondary_fermentation_start_day"
            ])
        elif stage == "PACKAGING":
            fields.extend([
                "packaging_date",
                "end_gravity",
                "beer_volume",
                "carbonation_type",
                "carbonation_level"
            ])
        return fields
