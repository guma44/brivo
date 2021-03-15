from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


from brivo.brew.models import BaseModel, MASS_UNITS
from brivo.utils.measures import BeerColor

from django_measurement.models import MeasurementField
from measurement.measures import Volume, Weight, Temperature

__all__ = ("Fermentable", "IngredientFermentable", "InventoryFermentable")


FERMENTABLE_TYPE = (
    ("ADJUNCT", "Adjunct"),
    ("GRAIN", "Grain"),
    ("DRY EXTRACT", "Dry extract"),
    ("LIQUID EXTRACT", "Liquid extract"),
    ("SUGAR", "Sugar"),
)

FERMENTABLE_USE = [
    ("MASHING", "Mashing"),
    ("BOIL", "Boil"),
    ("LATE BOIL", "Late boil"),
    ("STEEP", "Steep"),
]


class BaseFermentable(BaseModel):
    """Base class for fermentable.

    Frmentable encompasses all fermentable items that contribute
    substantially to the beer gravity including extracts, grains, sugars, honey, fruits.
    """

    type = models.CharField(
        _("Type"),
        max_length=255,
        choices=FERMENTABLE_TYPE,
        help_text="Fermentable type.",
    )
    color = MeasurementField(
        measurement=BeerColor,
        verbose_name=_("Color"),
        help_text="""The color of the item.""",
    )
    # yield
    extraction = models.DecimalField(
        _("Extraction"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="""Percent dry yield (fine grain) 
            for the grain, or the raw yield by weight if this is an 
            extract adjunct or sugar.""",
    )


class Fermentable(BaseFermentable):
    # oritin
    country = models.ForeignKey(
        "Country",
        verbose_name=_("Country"),
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    # Max in batch
    max_use = models.DecimalField(
        _("Max Use"),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="""The recommended 
            maximum percentage (by weight) this ingredient should represent in a 
            batch of beer.""",
    )
    description = models.TextField(
        _("Description"), max_length=255, blank=True, null=True
    )
    external_link = models.URLField(
        _("External Link"), max_length=255, blank=True, null=True
    )
    comment = models.TextField(_("Comment"), blank=True, null=True)
    active = models.BooleanField(_("Active"), default=True)


class InventoryFermentable(BaseFermentable):
    inventory = models.ForeignKey("brew.Inventory", verbose_name=_("Inventory"), on_delete=models.CASCADE, related_name="fermentables")
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    comment = models.TextField(_("Comment"))


class IngredientFermentable(BaseFermentable):
    recipe = models.ForeignKey(
        "brew.Recipe",
        verbose_name=_("Recipe"),
        on_delete=models.CASCADE,
        related_name="fermentables",
    )
    amount = MeasurementField(
        measurement=Weight,
        verbose_name=_("Amount"),
        unit_choices=MASS_UNITS,
        help_text="Weight of the fermentable, extract or sugar.",
    )
    use = models.CharField(
        _("Fermentable Use"), max_length=255, choices=FERMENTABLE_USE
    )
