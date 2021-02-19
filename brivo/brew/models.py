from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _



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
 ('MASHING', 'Mashing'),
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



class Yeast(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    short_link = models.CharField(_("Short link"), max_length=255)
    lab = models.CharField(_("Lab"), max_length=255)
    lab_id = models.CharField(_("Lab ID"), max_length=255)
    type = models.CharField(_("Type"), max_length=255)
    form = models.CharField(_("Form"), max_length=255)
    atten_min = models.DecimalField(_("Min Attenuation"), max_digits=5, decimal_places=2)
    atten_max = models.DecimalField(_("Max Attenuation"), max_digits=5, decimal_places=2)
    flocc = models.CharField(_("Flocculation"), max_length=255)
    temp_min = models.DecimalField(_("Min Temperature"), max_digits=5, decimal_places=2)
    temp_max = models.DecimalField(_("Max Temperature"), max_digits=5, decimal_places=2)
    alco_toler = models.CharField(_("Alcohol Toleration"), max_length=255)
    # Should be link to styles styles = models.CharField(_("Styles"), max_length=255)
    desc = models.CharField(_("Description"), max_length=255)
    external_link = models.CharField(_("External Link"), max_length=255)
    active = models.DecimalField(_("Active"), max_digits=5, decimal_places=2)


class Style(models.Model):
    category_id = models.CharField(_(""), max_length=255)
    category = models.CharField(_(""), max_length=255)
    short_link = models.CharField(_(""), max_length=255)
    name = models.CharField(_("Name"), max_length=255)
    og_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    og_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    fg_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    fg_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    ibu_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    ibu_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    color_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    color_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    alcohol_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    alcohol_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    ferm_type = models.CharField(_(""), max_length=255)
    desc_aroma = models.CharField(_(""), max_length=255)
    desc_appe = models.CharField(_(""), max_length=255)
    desc_flavor = models.CharField(_(""), max_length=255)
    desc_mouth = models.CharField(_(""), max_length=255)
    desc_overall = models.CharField(_(""), max_length=255)
    desc_comment = models.CharField(_(""), max_length=255)
    desc_ingre = models.CharField(_(""), max_length=255)
    desc_history = models.CharField(_(""), max_length=255)
    desc_style_comp = models.CharField(_(""), max_length=255)
    commercial_exam = models.CharField(_(""), max_length=255)
    tags = models.CharField(_(""), max_length=255)
    active = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=0)


class Fermentable(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    short_link = models.CharField(_(""), max_length=255)
    country = models.CharField(_(""), max_length=255)
    type = models.CharField(_(""), max_length=255, choices=FERMENTABLE_TYPE)
    color = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    extraction = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    max_use = models.DecimalField(_(""), max_digits=5, decimal_places=2)
    description = models.CharField(_(""), max_length=255)
    active = models.DecimalField(_(""), max_digits=5, decimal_places=2)


class Country(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    code = models.CharField(_("Code"), max_length=255)


class Batch(models.Model):
    # Operational fields
    stage = models.CharField(_("Stage"), max_length=50, choices=BATCH_STAGES, default="MASHING")
    recipe = models.ForeignKey("brew.Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    # Stage 1 fields: mashing
    name = models.CharField(_("Name"), max_length=255)
    batch_number = models.IntegerField(_("Batch Number"))
    brewing_day = models.DateField(_("Brewing Day"), auto_now=False, auto_now_add=False)
    grain_temperature = models.DecimalField(_("Grain Temperature"), max_digits=5, decimal_places=2)
    sparging_temperature = models.DecimalField(_("Sparging Temperature"), max_digits=5, decimal_places=2)

    # Stage 2 fields: boiling
    gravity_before_boil = models.DecimalField(_("Gravity Before Boil"), max_digits=5, decimal_places=2)

    # Stage 3 fields: primary fermentation
    initial_gravity = models.DecimalField(_("Initial Gravity"), max_digits=5, decimal_places=2)
    wort_volume = models.DecimalField(_("Wort Volume"), max_digits=5, decimal_places=2)
    boil_waists = models.DecimalField(_("Boil Waists"), max_digits=5, decimal_places=2)
    primary_fermentation_start_day = models.DateField(_("Primary Fermentation Start Day"), auto_now=False, auto_now_add=False)

    # Stage 4 fields: secondary fermentation
    secondary_fermentation_start_day = models.DateField(_("Secondary Fermentation Start Day"), auto_now=False, auto_now_add=False)
    gravity_after_primary_fermentation = models.DecimalField(_(""), max_digits=5, decimal_places=2)

    # Stage 4 fields: packaging
    packaging_date = models.DateField(_("Packaging Start Day"), auto_now=False, auto_now_add=False)
    end_gravity = models.DecimalField(_("End Gravity"), max_digits=5, decimal_places=2)
    beer_volume = models.DecimalField(_("Beer Volume"), max_digits=5, decimal_places=2)
    carbonation_type = models.CharField(_("Carbonation Type"), max_length=50, choices=CARBONATION_TYPE)
    carbonation_level = models.DecimalField(_("Carbonation Level"), max_digits=5, decimal_places=2)

    hidden_fields = ["stage"]
    required_fields = ["recipe",]

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


class Extra(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    short_link = models.CharField(_("Short Link"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=EXTRA_TYPE)
    desc = models.CharField(_("Description"), max_length=255)
    active = models.DecimalField(_("Active"), max_digits=5, decimal_places=2)


class Fermentable(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=FERMENTABLE_TYPE)
    color = models.DecimalField(_("Color"), max_digits=5, decimal_places=2)
    fermentable_yield = models.DecimalField(_("Yield"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])


class Hop(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    alpha_acids = models.DecimalField(_("Alpha Acids"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])


class Extra(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=EXTRA_TYPE)


class Yeast(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    lab = models.CharField(_(""), max_length=255)
    lab_id = models.CharField(_(""), max_length=255)
    type = models.CharField(_(""), max_length=255, choices=YEAST_TYPE)
    attenuation = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])


class Inventory(models.Model):
    user = models.OneToOneField("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    inventory_fermentable = models.ForeignKey("InventoryFermentable", verbose_name=_("Fermentable"), on_delete=models.CASCADE)
    inventory_yeast = models.ForeignKey("InventoryYeast", verbose_name=_("Yeast"), on_delete=models.CASCADE)
    inventory_hop = models.ForeignKey("InventoryHop", verbose_name=_("Hop"), on_delete=models.CASCADE)
    inventory_extra = models.ForeignKey("InventoryExtra", verbose_name=_("Extra"), on_delete=models.CASCADE)


class InventoryFermentable(Fermentable):
    amount = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])

class InventoryHop(Hop):
    amount = models.DecimalField(_("Amount"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]),
    form = models.CharField(_("Form"), max_length=255, choices=HOP_FORM)
    year = models.IntegerField(_("Year"), validators=[MinValueValidator(0)])


class InventoryYeast(Yeast):
    amount = models.DecimalField(_("Amount"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]),
    expiration_date = models.DateField(_("Expiration Date"), auto_now=False, auto_now_add=False)
    collected_at = models.DateField(_("Collected At"), auto_now=False, auto_now_add=False, blank=True)
    generation = models.CharField(_("Generation"), max_length=50, blank=True)
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)

class InventoryExtra(Extra):
    amount = models.DecimalField(_("Amount"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])


class FermentableIngredient(Fermentable):
    amount = models.DecimalField(_("Amount"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    use = models.CharField(_("Fermentable Use"), max_length=255, choices=FERMENTABLE_USE)


class HopIngredient(Hop):
    use = models.CharField(_("Use"), max_length=255, choices=HOP_USE)
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)


class YeastIngredient(Yeast):
    amount = models.DecimalField(_("Amount"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]),
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)


class ExtraIngredient(Extra):
    use = models.CharField(_("Use"), max_length=255, choices=EXTRA_USE)
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2)
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)


class Fermentation(models.Model):
    primary_fermentation_temperature = models.DecimalField(_("Primary Ferementation Temperature"), max_digits=5, decimal_places=2, default=17)
    secondary_fermentation_temperature = models.DecimalField(_("Secondary Fermentation Temperature"), max_digits=5, decimal_places=2, default=20)


class MashStep(models.Model):
    temperature = models.DecimalField(_("Temperature"), max_digits=5, decimal_places=2)
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, default=0)
    note = models.TextField(_("Note"), default="-")


class Recipe(models.Model):
    # user = 
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=RECIPE_TYPE)
    batch_volume = models.DecimalField(_("Batch Size"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]),
    mash_efficiency = models.DecimalField(_("Mash Efficiency"), max_digits=5, decimal_places=2, default=75)
    notes = models.CharField(_(""), max_length=255, default="-")
    fermentables = models.ForeignKey("FermentableIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    hops = models.ForeignKey("HopIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    yeasts = models.ForeignKey("YeastIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    extras = models.ForeignKey("ExtraIngredient", verbose_name=_(""), on_delete=models.CASCADE)
    mashing = models.ForeignKey("MashStep", verbose_name=_(""), on_delete=models.CASCADE)
