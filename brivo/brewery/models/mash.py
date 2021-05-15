from django.db import models
from django.utils.translation import gettext_lazy as _


from brivo.brewery.fields import TemperatureField
from brivo.brewery.models import BaseModel

from modelcluster.fields import ParentalKey

__all__ = ("MashStep",)


class MashStep(BaseModel):
    recipe = ParentalKey(
        "Recipe",
        verbose_name=_("Recipe"),
        on_delete=models.CASCADE,
        related_name="mash_steps",
    )
    temperature = TemperatureField(verbose_name=_("Temperature"))
    time = models.DecimalField(_("Time"), max_digits=5, decimal_places=2, default=0)
    note = models.TextField(_("Note"), blank=True, null=True)