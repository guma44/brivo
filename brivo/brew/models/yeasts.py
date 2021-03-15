from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from brivo.brew.models import BaseModel, MASS_UNITS

from django_measurement.models import MeasurementField
from measurement.measures import Weight, Temperature

__all__ = ("Yeast", "IngredientYeast", "InventoryYeast")


YEAST_TYPE = [
    ("ALE", "Ale"),
    ("LAGER", "Lager"),
    ("WHEAT", "Wheat"),
    ("WILD", "Wild"),
    ("CHAMPAGNE", "Champagne"),
    ("BACTERIA", "Bacteria"),
    ("MIX", "Mix"),
]


YEAST_FORM = [
    ("DRY", "Dry"),
    ("LIQUID", "Liquid"),
    ("SLURRY", "Slurry"),
    ("CULTURE", "Culture"),
]


class BaseYeast(BaseModel):
    lab = models.CharField(_("Lab"), max_length=255)
    type = models.CharField(_("Type"), max_length=255, choices=YEAST_TYPE)


class Yeast(BaseYeast):
    lab_id = models.CharField(_("Lab ID"), max_length=255)
    atten_min = models.DecimalField(
        _("Min Attenuation"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    atten_max = models.DecimalField(
        _("Max Attenuation"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    flocc = models.CharField(_("Flocculation"), max_length=255)
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)
    temp_min = MeasurementField(
        measurement=Temperature, verbose_name=_("Min Temperature")
    )
    temp_max = MeasurementField(
        measurement=Temperature, verbose_name=_("Max Temperature")
    )
    alco_toler = models.CharField(_("Alcohol Tolerance"), max_length=255)
    styles = models.CharField(_("Styles"), max_length=1000, blank=True, null=True)
    desc = models.CharField(_("Description"), max_length=255, blank=True, null=True)
    external_link = models.URLField(
        _("External Link"), max_length=255, blank=True, null=True
    )
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


class InventoryYeast(BaseYeast):
    inventory = models.ForeignKey("brew.Inventory", verbose_name=_("Inventory"), on_delete=models.CASCADE, related_name="yeasts")
    expiration_date = models.DateField(
        _("Expiration Date"), auto_now=False, auto_now_add=False
    )
    collected_at = models.DateField(
        _("Collected At"), auto_now=False, auto_now_add=False, blank=True
    )
    generation = models.CharField(_("Generation"), max_length=50, blank=True)
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    comment = models.TextField(_("Comment"))


class IngredientYeast(BaseYeast):
    recipe = models.ForeignKey(
        "brew.Recipe",
        verbose_name=_("brew.models.Recipe"),
        on_delete=models.CASCADE,
        related_name="yeasts",
    )
    amount = MeasurementField(
        measurement=Weight, verbose_name=_("Amount"), unit_choices=MASS_UNITS
    )
    attenuation = models.DecimalField(
        _("Attenuation"),
        max_digits=5,
        decimal_places=2,
        blank=True,
        default=75.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    form = models.CharField(_("Form"), max_length=255, choices=YEAST_FORM)
