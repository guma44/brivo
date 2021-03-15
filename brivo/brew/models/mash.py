from django.db import models
from django.utils.translation import gettext_lazy as _


from brivo.brew.models import BaseModel

from django_measurement.models import MeasurementField
from measurement.measures import Temperature

__all__ = ("MashStep", )


class MashStep(BaseModel):
    recipe = models.ForeignKey(
        "Recipe",
        verbose_name=_("Recipe"),
        on_delete=models.CASCADE,
        related_name="mash_steps",
    )
    temperature = MeasurementField(
        measurement=Temperature, verbose_name=_("Temperature")
    )
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, default=0)
    note = models.TextField(_("Note"), blank=True, null=True)