from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


from brivo.brewery.models import BaseModel, MASS_UNITS
from brivo.brewery.fields import BeerColorField, MassField

from modelcluster.fields import ParentalKey


__all__ = ("Fermentable", "IngredientFermentable", "InventoryFermentable")


FERMENTABLE_TYPE = (
    ("ADJUNCT", _("Adjunct")),
    ("GRAIN", _("Grain")),
    ("DRY EXTRACT", _("Dry extract")),
    ("LIQUID EXTRACT", _("Liquid extract")),
    ("SUGAR", _("Sugar")),
)

FERMENTABLE_USE = [
    ("MASHING", _("Mashing")),
    ("BOIL", _("Boil")),
    ("LATE BOIL", _("Late boil")),
    ("STEEP", _("Steep")),
]


class BaseFermentable(BaseModel):
    """Base class for fermentable.

    Frmentable encompasses all fermentable items that contribute
    substantially to the beer gravity including extracts, grains, sugars, honey, fruits.
    """

    type = models.CharField(
        _("Type"),
        max_length=1000,
        choices=FERMENTABLE_TYPE,
        # help_text="Fermentable type.",
    )
    color = BeerColorField(
        verbose_name=_("Color"),
        # help_text="""The color of the item.""",
    )
    # yield
    extraction = models.DecimalField(
        _("Extraction"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        # help_text="""Percent dry yield (fine grain)
        #     for the grain, or the raw yield by weight if this is an
        #     extract adjunct or sugar.""",
    )


class Fermentable(BaseFermentable):
    # origin
    country = ParentalKey(
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
        help_text=_("""The recommended 
            maximum percentage (by weight) this ingredient should represent in a 
            batch of beer."""),
    )
    description = models.TextField(
        _("Description"), max_length=1000, blank=True, null=True
    )
    external_link = models.URLField(
        _("External Link"), max_length=1000, blank=True, null=True
    )
    comment = models.TextField(_("Comment"), blank=True, null=True)
    active = models.BooleanField(_("Active"), default=True)


class InventoryFermentable(BaseFermentable):
    inventory = models.ForeignKey(
        "brewery.Inventory",
        verbose_name=_("Inventory"),
        on_delete=models.CASCADE,
        related_name="fermentables",
    )
    amount = MassField(verbose_name=_("Amount"), unit_choices=MASS_UNITS)
    comment = models.TextField(_("Comment"))


class IngredientFermentable(BaseFermentable):
    recipe = ParentalKey(
        "brewery.Recipe",
        verbose_name=_("Recipe"),
        on_delete=models.CASCADE,
        related_name="fermentables",
    )
    amount = MassField(
        verbose_name=_("Amount"),
        unit_choices=MASS_UNITS,
        help_text=_("Weight of the fermentable, extract or sugar."),
    )
    use = models.CharField(
        _("Fermentable Use"), max_length=1000, choices=FERMENTABLE_USE
    )
