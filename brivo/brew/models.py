from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _



FERMENTABLE_CHOICES = [(s.upper(), s) for s in ['Adjunct', 'Base malt', 'Crystal malt', 'Dry extract', 'Liquid extract', 'Roasted malt', 'Sugar']]
BATCH_STAGES = (
    ("MASHING", "Mashing"),
    ("BOILING", "Boiling"),
    ("PRIMARY_FERMENTATION", "Primary Fermentation"),
    ("SECONDARY_FERMENTATION", "Secondary Fermentation"),
    ("PACKAGING", "Packaging"),
    ("FINISHED", "Finished")
)

CARBONATION_TYPE = (
    ("FORCED", "forced"),
    ("REFERMENTATION", "refermentation")
)


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
    name = models.CharField(_(""), max_length=255)
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
    name = models.CharField(_(""), max_length=255)
    short_link = models.CharField(_(""), max_length=255)
    country = models.CharField(_(""), max_length=255)
    type = models.CharField(_(""), max_length=255, choices=FERMENTABLE_CHOICES)
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
    recipe = models.ForeignKey("brivo.brew.models.Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE)
    user = models.ForeignKey("brivo.users.models.User", verbose_name=_("User"), on_delete=models.CASCADE)
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




# class Extra(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         short_link = models.CharField(_(""), max_length=255)
#         type = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Any', 'Spice', 'Flavor', 'Fining', 'Herb', 'Water additive', 'Other']
#                 }
#             ]
#         use = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Boil', 'Mash', 'Primary', 'Secondary', 'Keging', 'Bottling', 'Other']
#                 }
#             ]
#         desc = models.CharField(_(""), max_length=255)
#         active = models.DecimalField(_(""), max_digits=5, decimal_places=2)


# class FermentableInventory = BaseFermentable.inherit({
#         user_id = models.CharField(_(""), max_length=255)



# class HopInventory = BaseHop.inherit({
#         user_id = models.CharField(_(""), max_length=255)



# class YeastInventory = BaseYeast.inherit({
#         user_id = models.CharField(_(""), max_length=255)



# class ExtraInventory = BaseExtra.inherit({
#         user_id = models.CharField(_(""), max_length=255)



# class BaseFermentable(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         type = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Adjunct', 'Base malt', 'Crystal malt', 'Dry extract', 'Liquid extract', 'Roasted malt', 'Sugar']
#                 }
#             ]
#         amount = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'gt',
#                     param: 0
#                 }
#             ]
#         color = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         extraction = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'range',
#                     param: [0, 100]
#                 }
#             ]


# class BaseHop(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         form = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Hop pellets', 'Whole hops', 'Extract']
#                 }
#             ]
#         amount = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'gt',
#                     param: 0
#                 }
#             ]
#         alpha = models.DecimalField(_(""), max_digits=5, decimal_places=2)


# class BaseExtra(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         type = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Any', 'Spice', 'Flavor', 'Fining', 'Herb', 'Water additive']
#                 }
#             ]
#         amount = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'gt',
#                     param: 0
#                 }
#             ]
#         amount_unit = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['mg', 'g', 'kg', 'oz', 'lb', 'tsp', 'tbsp', 'gal', 'l', 'ml', 'pt', 'qt', 'floz', 'pcs']
#                 }
#             ]


# class BaseYeast(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         lab = models.CharField(_(""), max_length=255)
#         lab_id = models.CharField(_(""), max_length=255)
#         type = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Ale', 'Lager', 'Wild', 'Bacteria', 'Mix']
#                 }
#             ]
#         form = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Dry', 'Liquid', 'Slurry', 'Culture']
#                 }
#             ]
#         attenuation = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         amount = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'gt',
#                     param: 0
#                 }
#             ]
#         amount_unit = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['mg', 'g', 'kg', 'oz', 'lb', 'tsp', 'tbsp', 'gal', 'l', 'ml', 'pt', 'qt', 'floz', 'pcs']
#                 }
#             ]


# class FermentableIngredient = BaseFermentable.inherit({
#         inventory_id = models.CharField(_(""), max_length=255)
#             optional: true
#         use = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Mashing', 'Boiling', 'Late boiling', 'Steep']
#                 }
#             ]
#     }


# class HopIngredient = BaseHop.inherit({
#         inventory_id = models.CharField(_(""), max_length=255)
#             optional: true
#         use = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Boiling', 'Dry hop', 'Mashing', 'First wort', 'Whirpool']
#                 }
#             ]
#         time = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'gt',
#                     param: 0
#                 }
#             ]


# class YeastIngredient = BaseYeast.inherit({
#         inventory_id = models.CharField(_(""), max_length=255)
#             optional: true


# class ExtraIngredient = BaseExtra.inherit({
#         inventory_id = models.CharField(_(""), max_length=255)
#             optional: true
#         use = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['Boiling', 'Mashing', 'Primary fermentation', 'Secondary fermentation', 'Keg', 'Bottling']
#                 }
#             ]
#         time = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         time_unit = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['minute', 'hour', 'day', 'week', 'month', 'year']
#                 }
#             ]


# class Fermentation(models.Model):
#         yeast_temperature = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=22)
#         yeast_type = models.CharField(_(""), max_length=255, default='Yeast rehydratation')
#         fermentation_days_warm = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=7)
#         fermentation_warm_min_temp = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=18)
#         fermentation_warm_max_temp = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=21)
#         fermentation_days_cool = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=10)
#         fermentation_cool_min_temp = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=17)
#         fermentation_cool_max_temp = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=20)
#     },


# class DisplayInfo(models.Model):
#         og = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         fg = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         bitt_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         bitt_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         percentage_og = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
#         percentage_fg = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
#         percentage_color = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
#         percentage_ibu = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
#         percentage_bitterness = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
#         percentage_alcohol = models.DecimalField(_(""), max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)]),
#     resolveError({nestedName, validator}) {
#         if (validator == 'required') {
#             return `Please provide ${nestedName} for recipe DisplayInfo`;,

# class StyleInfo(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         short_link = models.CharField(_(""), max_length=255)
#         alcohol_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         alcohol_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         color_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         color_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         fg_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         fg_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         ibu_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         ibu_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         og_max = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         og_min = models.DecimalField(_(""), max_digits=5, decimal_places=2)


# class MashStep(models.Model):
#         step = models.CharField(_(""), max_length=255)
#         note = models.TextField(_(""), default="-")
#         temperature = models.DecimalField(_(""), max_digits=5, decimal_places=2)
#         time = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=0)
#         type = models.CharField(_(""), max_length=255)

# class Mash(models.Model):
#         water_ratio = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=2.5)
#         boling_time = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=60)
#         steps = 
#             type: [MashStep],
#             default() {
#                 return [];
#             }


# class ERROR_MESSAGES = {
#     Name: 'Fill title',
#     StyleName: 'Choose a style of beer',
#     Type: 'Choose a brewing method from: All grain, All extract or Partial mash',
#     BatchVolume: 'Fill batch volume',
#     BatchVolumeUnit: 'Choose unit of batch volume',
#     Efficiency: 'Fill efficiency',
#     Bitterness: 'Wrong bitterness',
#     Alcohol: 'Wrong alcohol',
# }


# class BaseRecipe(models.Model):
#         name = models.CharField(_(""), max_length=255)
#         type = models.CharField(_(""), max_length=255)
#             validators: [
#                 {
#                     type: 'choice',
#                     param: ['All grain', 'All extract', 'Partial mash'],
#                     message: 'Available brewing methods are: All grain, All extract and Partial mash'
#                 }
#             ]
#         batch_volume = models.DecimalField(_(""), max_digits=5, decimal_places=2),
#             validators: [
#                 {
#                     type: 'gt',
#                     param: 0,
#                     message: 'Volume has to be a positive number'
#                 }
#             ]
#         efficiency = models.DecimalField(_(""), max_digits=5, decimal_places=2, default=75)
#             validators: [
#                 {
#                     type: 'range',
#                     param: [0, 100]
#                 }
#             ]
#         notes = models.CharField(_(""), max_length=255, default="-")
#         style_info = 
#             type: StyleInfo
#         fermentables = 
#             type: [FermentableIngredient],
#             validators: [
#                 {
#                     type: 'minLength',
#                     param: 1,
#                     message: 'Choose at least one fermentable'
#                 }
#             ],
#             default() {
#                 return [];
#             }
#         hops = 
#             type: [HopIngredient],
#             validators: [
#                 {
#                     type: 'minLength',
#                     param: 1,
#                     message: 'Choose at least one hop'
#                 }
#             ],
#             default() {
#                 return [];
#             }
#         yeasts = 
#             type: [YeastIngredient],
#             validators: [
#                 {
#                     type: 'minLength',
#                     param: 1,
#                     message: 'Choose at least one yeast'
#                 }
#             ],
#             default() {
#                 return [];
#             }
#         extras = 
#             type: [ExtraIngredient],
#             default() {
#                 return [];
#             }
#         mashing = 
#             type: Mash,
#             default() {
#                 return new Mash();
#             }
#         suggested_fermentation = 
#             type: Fermentation,
#             default() {
#                 return new Fermentation();
#             }
#         public = models.BooleanField(_(""), default=false)
#         user_id = models.CharField(_(""), max_length=255)
