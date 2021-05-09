from django.db import models
from django.utils.translation import gettext_lazy as _

from brivo.brew.models import BaseModel, MASS_UNITS, TIME_CHOICE

from modelcluster.fields import ParentalKey
from django_measurement.models import MeasurementField
from measurement.measures import Weight

__all__ = ("Extra", "IngredientExtra", "InventoryExtra")


EXTRA_TYPE = [
    ("ANY", "Any"),
    ("SPICE", "Spice"),
    ("FLAVOR", "Flavor"),
    ("FINING", "Fining"),
    ("HERB", "Herb"),
    ("WATER AGENT", "Water agent"),
    ("OTHER", "Other"),
]

EXTRA_USE = [
    ("BOIL", "Boil"),
    ("MASH", "Mash"),
    ("PRIMARY", "Primary"),
    ("SECONDARY", "Secondary"),
    ("KEGING", "Keging"),
    ("BOTTLING", "Bottling"),
    ("OTHER", "Other"),
]


class BaseExtra(BaseModel):
    type = models.CharField(_("Type"), max_length=1000, choices=EXTRA_TYPE)
    use = models.CharField(_("Use"), max_length=1000, choices=EXTRA_USE)


class Extra(BaseExtra):
    desc = models.CharField(_("Description"), max_length=1000)
    active = models.DecimalField(_("Active"), max_digits=5, decimal_places=2)


class InventoryExtra(BaseExtra):
    inventory = models.ForeignKey(
        "brew.Inventory",
        verbose_name=_("Inventory"),
        on_delete=models.CASCADE,
        related_name="extras",
    )
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    comment = models.TextField(_("Comment"))


class IngredientExtra(BaseExtra):
    recipe = ParentalKey(
        "brew.Recipe",
        verbose_name=_("Recipe"),
        on_delete=models.CASCADE,
        related_name="extras",
    )
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2)
    time_unit = models.CharField(_("Time Unit"), max_length=1000, choices=TIME_CHOICE)
