from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from brivo.brew.models import BaseModel, MASS_UNITS, TIME_CHOICE

from django_measurement.models import MeasurementField
from measurement.measures import Weight

__all__ = ("Hop", "IngredientHop", "InventoryHop")


HOP_USE = [
    ("BOIL", "Boil"),
    ("DRY HOP", "Dry hop"),
    ("MASH", "Mash"),
    ("AROMA", "Aroma"),
    ("FIRST WORT", "First wort"),
    ("WHIRPOOL", "Whirpool"),
]


HOP_FORM = [
    ("HOP PELLETS", "Hop pellets"),
    ("WHOLE HOPS", "Whole hops"),
    ("EXTRACT", "Extract"),
]

HOP_TYPE = [
    ("DUAL PURPOSE", "Dual Purpose"),
    ("AROMA", "Aroma"),
    ("BITTERING", "Bittering"),
]


class BaseHop(BaseModel):

    alpha_acids = models.DecimalField(
        _("Alpha Acids"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )


class Hop(BaseHop):
    country = models.ForeignKey(
        "Country",
        verbose_name=_("Country"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    external_link = models.URLField(
        _("External Link"), max_length=255, blank=True, null=True
    )
    alpha_min = models.DecimalField(
        _("Alpha Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    alpha_max = models.DecimalField(
        _("Alpha Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    beta_min = models.DecimalField(
        _("Beta Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    beta_max = models.DecimalField(
        _("Beta Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    co_humulone_min = models.DecimalField(
        _("Co-Humulone Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    co_humulone_max = models.DecimalField(
        _("Co-Humulone Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    total_oil_min = models.DecimalField(
        _("Total Oil Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    total_oil_max = models.DecimalField(
        _("Total Oil Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    myrcene_min = models.DecimalField(
        _("Myrcene Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    myrcene_max = models.DecimalField(
        _("Myrcene Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    humulene_min = models.DecimalField(
        _("Humulene Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    humulene_max = models.DecimalField(
        _("Humulene Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    caryophyllene_min = models.DecimalField(
        _("Caryophyllene Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    caryophyllene_max = models.DecimalField(
        _("Caryophyllene Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    farnesene_min = models.DecimalField(
        _("Farnesene Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    farnesene_max = models.DecimalField(
        _("Farnesene Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    type = models.CharField(_("Type"), max_length=50, choices=HOP_TYPE)
    substitute = models.ManyToManyField(
        "Hop", verbose_name=_("Substitue"), blank=True, null=True
    )
    description = models.TextField(
        _("Description"), max_length=255, blank=True, null=True
    )
    comment = models.TextField(_("Comment"), blank=True, null=True)
    active = models.BooleanField(_("Active"), default=True)


class InventoryHop(BaseHop):
    inventory = models.ForeignKey("brew.Inventory", verbose_name=_("Inventory"), on_delete=models.CASCADE, related_name="hops")
    year = models.IntegerField(_("Year"), validators=[MinValueValidator(0)])
    form = models.CharField(_("Form"), max_length=255, choices=HOP_FORM)
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    comment = models.TextField(_("Comment"))


class IngredientHop(BaseHop):
    recipe = models.ForeignKey(
        "brew.Recipe",
        verbose_name=_("Recipe"),
        on_delete=models.CASCADE,
        related_name="hops",
    )
    use = models.CharField(_("Use"), max_length=255, choices=HOP_USE)
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    time = models.DecimalField(
        _("Time"), max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )
    time_unit = models.CharField(_("Time Unit"), max_length=255, choices=TIME_CHOICE)
