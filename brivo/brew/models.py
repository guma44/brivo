from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.deletion import DO_NOTHING
from django.db.models.fields import CharField
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_measurement.models import MeasurementField
from measurement.measures import Volume, Weight, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.utils import functions
from brivo.users.models import User


FERMENTABLE_TYPE = (
    ('ADJUNCT', 'Adjunct'),
    ('GRAIN', "Grain"),
    ('DRY EXTRACT', 'Dry extract'),
    ('LIQUID EXTRACT', 'Liquid extract'),
    ('SUGAR', 'Sugar')
)


BATCH_STAGES = (
    ("MASHING", "Mashing"),
    ("BOIL", "Boil"),
    ("PRIMARY FERMENTATION", "Primary Fermentation"),
    ("SECONDARY FERMENTATION", "Secondary Fermentation"),
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
 ('BOIL', 'Boil'),
 ('LATE BOIL', 'Late boil'),
 ('STEEP', 'Steep')]


HOP_USE = [('BOIL', 'Boil'),
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

HOP_TYPE = [
    ("DUAL PURPOSE", "Dual Purpose"),
    ("AROMA", "Aroma"),
    ("BITTERING", "Bittering")
]


YEAST_TYPE = [
    ('ALE', 'Ale'),
    ('LAGER', 'Lager'),
    ('WHEAT', 'Wheat'),
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


RECIPE_TYPE = [('ALL GRAIN', 'All Grain'),
 ('EXTRACT', 'Extract'),
 ('PARTIAL MASH', 'Partial Mash')
]

MASS_UNITS = (
    ('g', 'g'),
    ('kg', 'Kg'),
    ('oz', 'oz'),
    ('lb', 'lb'))

VOLUME_UNITS = (
    ('l', 'l'),
    ('ml', 'ml'),
    ('us_oz', 'US oz'), ('us_g', 'US Gal'))

class Tag(models.Model):
    name = models.CharField(_("Name"), max_length=255)

    def __str__(self):
        return self.name

class BaseFermentable(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=FERMENTABLE_TYPE)
    color = MeasurementField(measurement=BeerColor, verbose_name=_("Color"))
    extraction = models.DecimalField(_("Extraction"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.name


class BaseExtra(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=EXTRA_TYPE)
    use = models.CharField(_("Use"), max_length=255, choices=EXTRA_USE)

    def __str__(self):
        return self.name


class Extra(BaseExtra):
    desc = models.CharField(_("Description"), max_length=255)
    active = models.DecimalField(_("Active"), max_digits=5, decimal_places=2)


class Fermentable(BaseFermentable):
    country = models.ForeignKey("Country", verbose_name=_("Country"), on_delete=models.CASCADE, blank=True, null=True)
    max_use = models.DecimalField(_("Max Use"), max_digits=5, decimal_places=2, blank=True, null=True)
    description = models.TextField(_("Description"), max_length=255, blank=True, null=True)
    external_link = models.URLField(_("External Link"), max_length=255, blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)
    active = models.BooleanField(_("Active"), default=True)

    def __str__(self):
        return self.name


class BaseHop(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    alpha_acids = models.DecimalField(_("Alpha Acids"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return self.name
    


class Hop(BaseHop):
    country = models.ForeignKey("Country", verbose_name=_("Country"), on_delete=models.CASCADE, blank=True, null=True)
    external_link = models.URLField(_("External Link"), max_length=255, blank=True, null=True)
    alpha_min = models.DecimalField(_("Alpha Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    alpha_max = models.DecimalField(_("Alpha Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    beta_min = models.DecimalField(_("Beta Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    beta_max = models.DecimalField(_("Beta Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    co_humulone_min = models.DecimalField(_("Co-Humulone Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    co_humulone_max = models.DecimalField(_("Co-Humulone Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    total_oil_min = models.DecimalField(_("Total Oil Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    total_oil_max = models.DecimalField(_("Total Oil Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    myrcene_min = models.DecimalField(_("Myrcene Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    myrcene_max = models.DecimalField(_("Myrcene Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    humulene_min = models.DecimalField(_("Humulene Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    humulene_max = models.DecimalField(_("Humulene Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    caryophyllene_min = models.DecimalField(_("Caryophyllene Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    caryophyllene_max = models.DecimalField(_("Caryophyllene Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    farnesene_min = models.DecimalField(_("Farnesene Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    farnesene_max = models.DecimalField(_("Farnesene Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    type = models.CharField(_("Type"), max_length=50, choices=HOP_TYPE)
    substitute = models.ManyToManyField("Hop", verbose_name=_("Substitue"), blank=True, null=True)
    description = models.TextField(_("Description"), max_length=255, blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)
    active = models.BooleanField(_("Active"), default=True)


class BaseYeast(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    lab = models.CharField(_("Lab"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=YEAST_TYPE)

    def __str__(self):
        return self.name


class Yeast(BaseYeast):
    lab_id = models.CharField(_("Lab ID"), max_length=255)
    atten_min = models.DecimalField(_("Min Attenuation"), max_digits=5, decimal_places=2, blank=True, null=True)
    atten_max = models.DecimalField(_("Max Attenuation"), max_digits=5, decimal_places=2, blank=True, null=True)
    flocc = models.CharField(_("Flocculation"), max_length=255)
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)
    temp_min = MeasurementField(measurement=Temperature, verbose_name=_("Min Temperature"))
    temp_max = MeasurementField(measurement=Temperature, verbose_name=_("Max Temperature"))
    alco_toler = models.CharField(_("Alcohol Tolerance"), max_length=255)
    styles = models.CharField(_("Styles"), max_length=1000, blank=True, null=True)
    desc = models.CharField(_("Description"), max_length=255, blank=True, null=True)
    external_link = models.URLField(_("External Link"), max_length=255, blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)
    active = models.BooleanField(_("Active"), default=True)

    def get_average_attenuation(self):
        has_min = self.atten_min is not None
        has_max = self.atten_max is not None
        if has_min and has_max:
            return (float(self.atten_min) + float(self.atten_max)) / 2.0
        elif has_min:
            return float(self.atten_min)
        elif has_max:
            return float(self.atten_max)
        else:
            return 75.0


class Style(models.Model):
    category_id = models.CharField(_("Catetory ID"), max_length=255)
    category = models.CharField(_("Category"), max_length=255)
    name = models.CharField(_("Name"), max_length=255)
    og_min = MeasurementField(measurement=BeerGravity, verbose_name=_("OG Max"), blank=True, null=True)
    og_max = MeasurementField(measurement=BeerGravity, verbose_name=_("OG Min"), blank=True, null=True)
    fg_min = MeasurementField(measurement=BeerGravity, verbose_name=_("FG Max"), blank=True, null=True)
    fg_max = MeasurementField(measurement=BeerGravity, verbose_name=_("FG Min"), blank=True, null=True)
    ibu_min = models.DecimalField(_("IBU Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    ibu_max = models.DecimalField(_("IBU Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    color_min = MeasurementField(measurement=BeerColor, verbose_name=_("Color Min"), blank=True, null=True)
    color_max = MeasurementField(measurement=BeerColor, verbose_name=_("Color Max"), blank=True, null=True)
    alcohol_min = models.DecimalField(_("Alcohol Min"), max_digits=5, decimal_places=2, blank=True, null=True)
    alcohol_max = models.DecimalField(_("Alcohol Max"), max_digits=5, decimal_places=2, blank=True, null=True)
    ferm_type = models.CharField(_("Fermentation Type"), max_length=255, blank=True, null=True)
    desc_aroma = models.TextField(_("Aroma"), max_length=255, blank=True, null=True)
    desc_appe = models.TextField(_("Appearance"), max_length=255, blank=True, null=True)
    desc_flavor = models.TextField(_("Flavour"), max_length=255, blank=True, null=True)
    desc_mouth = models.TextField(_("Mouthfeel"), max_length=255, blank=True, null=True)
    desc_overall = models.TextField(_("Overall"), max_length=255, blank=True, null=True)
    desc_comment = models.TextField(_("Comment"), blank=True, null=True)
    desc_history = models.TextField(_("History"), max_length=255, blank=True, null=True)
    desc_ingre = models.TextField(_("Ingredients"), max_length=255, blank=True, null=True)
    desc_style_comp = models.TextField(_("Style Comparison"), max_length=255, blank=True, null=True)
    commercial_exam = models.TextField(_("Examples"), max_length=255, blank=True, null=True)
    tags = models.ManyToManyField("Tag")
    active = models.BooleanField(_("Active"), default=True)

    def get_og(self):
        if self.og_min is not None and self.og_max is not None:
            return (self.og_min + self.og_max) / 2.0
        elif self.og_min is not None:
            return self.og_min
        elif self.og_max is not None:
            return self.og_max
        else:
            return BeerGravity(0.0)

    def get_ibu(self):
        if self.ibu_min is not None and self.ibu_max is not None:
            return float(self.ibu_min + self.ibu_max) / 2.0
        elif self.ibu_min is not None:
            return self.ibu_min
        elif self.ibu_max is not None:
            return self.ibu_max
        else:
            return None

    def get_hex_color(self):
        if self.color_min is not None and self.color_max is not None:
            return functions.get_hex_color_from_srm(((self.color_min + self.color_max) / 2.0).srm)
        elif self.color_min is not None:
            return functions.get_hex_color_from_srm(self.color_min.srm)
        elif self.color_max is not None:
            return functions.get_hex_color_from_srm(self.color_max.srm)
        else:
            return ""

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    code = models.CharField(_("Code"), max_length=255)

    def __str__(self):
        return f"{self.name} ({self.code})"
    

class InventoryFermentable(BaseFermentable):
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))

class InventoryHop(BaseHop):
    year = models.IntegerField(_("Year"), validators=[MinValueValidator(0)])
    form = models.CharField(_("Form"), max_length=255, choices=HOP_FORM)
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))


class InventoryYeast(BaseYeast):
    expiration_date = models.DateField(_("Expiration Date"), auto_now=False, auto_now_add=False)
    collected_at = models.DateField(_("Collected At"), auto_now=False, auto_now_add=False, blank=True)
    generation = models.CharField(_("Generation"), max_length=50, blank=True)
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))

class InventoryExtra(BaseExtra):
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    comment = models.TextField(_("Comment"))


class Inventory(models.Model):
    user = models.OneToOneField("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    inventory_fermentable = models.ForeignKey("InventoryFermentable", verbose_name=_("Fermentable"), on_delete=models.CASCADE)
    inventory_yeast = models.ForeignKey("InventoryYeast", verbose_name=_("Yeast"), on_delete=models.CASCADE)
    inventory_hop = models.ForeignKey("InventoryHop", verbose_name=_("Hop"), on_delete=models.CASCADE)
    inventory_extra = models.ForeignKey("InventoryExtra", verbose_name=_("Extra"), on_delete=models.CASCADE)


class Recipe(models.Model):
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    # Recipe info
    style = models.ForeignKey("Style", verbose_name=_("Style"), on_delete=models.DO_NOTHING)
    type = models.CharField(_("Type"), max_length=255, choices=RECIPE_TYPE)
    name = models.CharField(_("Name"), max_length=255)

    # Batch info
    expected_beer_volume = MeasurementField(measurement=Volume, verbose_name=_("Expected Beer Volume"), unit_choices=VOLUME_UNITS, validators=[MinValueValidator(0)])
    boil_time = models.IntegerField(_("Boil Time"), default=60.0)
    evaporation_rate = models.DecimalField(_("Evaporation Rate"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=10.0)
    boil_loss = models.DecimalField(_("Boil Loss"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=10.0)
    trub_loss = models.DecimalField(_("Trub Loss"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=5.0)
    dry_hopping_loss = models.DecimalField(_("Dry Hopping Loss"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    # Mashing
    mash_efficiency = models.DecimalField(_("Mash Efficiency"), max_digits=5, decimal_places=2, default=75.0)
    liquor_to_grist_ratio = models.DecimalField(_("Liquor-To-Grist Ratio"), max_digits=5, decimal_places=2, default=3.0)
    # Rest
    note = models.TextField(_("Note"), max_length=255, blank=True)
    is_public = models.BooleanField(_("Public"), default=True)


    def get_initial_size(self):
        volume = self.expected_beer_volume.l
        boil_loss = volume * (float(self.boil_loss)/100.0)
        trub_loss = volume * (float(self.trub_loss)/100.0)
        dry_hopping_loss = volume * (float(self.dry_hopping_loss)/100.0)
        volume = volume + boil_loss + trub_loss + dry_hopping_loss
        return Volume(l=volume)


    def get_boil_size(self):
        initial_size = self.get_initial_size()
        volume = initial_size + (initial_size * (float(self.evaporation_rate)/100.0))
        return volume

    def get_pre_boil_gravity(self):
        pass

    def get_primary_size(self):
        pass

    def get_secondary_size(self):
        pass

    def get_color(self):
        added_colors = []
        for fermentable in self.fermentables.all():
            if fermentable.color.srm > 0 and fermentable.amount.kg > 0:
                added_colors.append(functions.calculate_mcu(
                    color=fermentable.color.srm,
                    weigth=fermentable.amount.kg,
                    volume=self.expected_beer_volume.l))
        return BeerColor(srm=functions.morey_equation(sum(added_colors)))

    def get_hex_color(self):
        return functions.get_hex_color_from_srm(self.get_color().srm)

    def get_volume_unit(self):
        if self.user.profile.general_units.lower() == "metric":
            return "l"
        else:
            return "us_g"

    def get_max_attenuation(self):
        min_val = 100
        for yeast in self.yeasts.all():
            if yeast.attenuation < min_val:
                min_val = yeast.attenuation
        return float(min_val) / 100

    def get_final_gravity(self):
        return self.get_gravity().plato * (1 - self.get_max_attenuation())

    def get_abv(self):
        return (self.get_gravity().plato - self.get_final_gravity()) * 0.516

    def get_grain_sugars(self):
        sugars = Weight(kg=0.0)
        for fermentable in self.fermentables.filter(type="GRAIN"):
            sugars += fermentable.get_fermentable_sugar()
        return Weight(kg=sugars.kg)

    def get_other_sugars(self):
        sugars = Weight(kg=0.0)
        for fermentable in self.fermentables.filter(~Q(type="GRAIN")):
            sugars += fermentable.get_fermentable_sugar()
        return Weight(kg=sugars.kg)

    def get_gravity(self):
        eff = float(self.mash_efficiency)
        grain_sugars = self.get_grain_sugars().kg * eff
        other_sugars = self.get_other_sugars().kg * 100.0
        grain_gravity = grain_sugars / (self.get_initial_size().l - grain_sugars / 145.0 + grain_sugars / 100.0)
        other_gravity = other_sugars / (self.get_initial_size().l - other_sugars / 145.0 + other_sugars / 100.0)
        # print(f"{self.name} [{self.get_initial_size().l}] - Grain gravity: {grain_gravity}, Other gravity: {other_gravity}, {eff}")
        return BeerGravity(plato=(grain_gravity + other_gravity)) 

    def get_ibu(self):
        added_ibus = []
        for hop in self.hops.all():
            if hop.use in ["BOIL", "AROMA", "FIRST WORT", "WHIRLPOOL"]:
                if hop.amount.g > 0 and hop.time > 0 and hop.alpha_acids > 0:
                    if self.name == "Just Like A Water":
                        print(f"Adding to {self.name}")
                    added_ibus.append(functions.calculate_ibu_tinseth(
                        og=self.get_gravity().sg,
                        time=float(hop.time),
                        type="PELLETS",
                        alpha=float(hop.alpha_acids),
                        weight=hop.amount.g,
                        volume=self.get_initial_size().l))
        return sum(added_ibus)
        

    def get_bitterness(self):
        pass

    def get_bitterness_ratio(self):
        pass

    def get_mash_size(self):
        pass

    def get_total_mash_volume(self):
        pass

    def __str__(self):
        return self.name


class FermentableIngredient(BaseFermentable):
    recipe = models.ForeignKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE, related_name="fermentables")
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    use = models.CharField(_("Fermentable Use"), max_length=255, choices=FERMENTABLE_USE)

    def get_fermentable_sugar(self):
        sugar = self.amount.kg * float(self.extraction) / 100.0
        return Weight(kg=sugar)

class HopIngredient(BaseHop):
    recipe = models.ForeignKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE, related_name="hops")
    use = models.CharField(_("Use"), max_length=255, choices=HOP_USE)
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)


class YeastIngredient(BaseYeast):
    recipe = models.ForeignKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE, related_name="yeasts")
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    attenuation = models.DecimalField(_("Attenuation"), max_digits=5, decimal_places=2, blank=True, default=75.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)


class ExtraIngredient(BaseExtra):
    recipe = models.ForeignKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE, related_name="extras")
    amount = MeasurementField(measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS, validators=[MinValueValidator(0)])
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2)
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)


class Fermentation(models.Model):
    primary_fermentation_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Primary Ferementation Temperature"), default=17)
    secondary_fermentation_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Secondary Fermentation Temperature"), default=20)


class MashStep(models.Model):
    recipe = models.ForeignKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE, related_name="mash_steps")
    temperature = MeasurementField(measurement=Temperature, verbose_name=_("Temperature"))
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, default=0)
    note = models.TextField(_("Note"), blank=True)


class Batch(models.Model):
    # Operational fields
    stage = models.CharField(_("Stage"), max_length=50, choices=BATCH_STAGES, default="MASHING")
    recipe = models.ForeignKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    # Stage 1 fields: info and mashing
    name = models.CharField(_("Name"), max_length=255)
    batch_number = models.IntegerField(_("Batch Number"))
    brewing_day = models.DateField(_("Brewing Day"), auto_now=False, auto_now_add=False)
    grain_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Grain Temperature"))
    sparging_temperature = MeasurementField(measurement=Temperature, verbose_name=_("Sparging Temperature"))

    # Stage 2 fields: boil
    gravity_before_boil = MeasurementField(measurement=BeerGravity, verbose_name=_("Gravity Before Boil"))

    # Stage 3 fields: primary fermentation
    initial_gravity = MeasurementField(measurement=BeerGravity, verbose_name=_("Initial Gravity"))
    wort_volume = MeasurementField(measurement=Volume, verbose_name=_("Wort Volume"), unit_choices=VOLUME_UNITS, validators=[MinValueValidator(0)])
    boil_waists = models.DecimalField(_("Boil Waists"), max_digits=5, decimal_places=2)
    primary_fermentation_start_day = models.DateField(_("Primary Fermentation Start Day"), auto_now=False, auto_now_add=False)

    # Stage 4 fields: secondary fermentation
    secondary_fermentation_start_day = models.DateField(_("Secondary Fermentation Start Day"), auto_now=False, auto_now_add=False)
    post_primary_fermentation = models.DecimalField(_("Post-primary Gravity"), max_digits=5, decimal_places=2)

    # Stage 4 fields: packaging
    packaging_date = models.DateField(_("Packaging Start Day"), auto_now=False, auto_now_add=False)
    end_gravity = MeasurementField(measurement=BeerGravity, verbose_name=_("End Gravity"))
    beer_volume = MeasurementField(measurement=Volume, verbose_name=_("Beer Volume"), unit_choices=VOLUME_UNITS, validators=[MinValueValidator(0)])
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
        elif stage == "BOIL":
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
