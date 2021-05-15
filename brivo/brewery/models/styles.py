from django.db import models
from django.utils.translation import gettext_lazy as _

from brivo.brewery.models import BaseModel
from brivo.utils import functions
from brivo.utils.measures import BeerGravity, BeerColor
from brivo.brewery.fields import BeerGravityField, BeerColorField

__all__ = ("Style",)


class Style(BaseModel):
    category_id = models.CharField(_("Catetory ID"), max_length=1000)
    category = models.CharField(_("Category"), max_length=1000)
    og_min = BeerGravityField(verbose_name=_("OG Max"), blank=True, null=True)
    og_max = BeerGravityField(verbose_name=_("OG Min"), blank=True, null=True)
    fg_min = BeerGravityField(verbose_name=_("FG Max"), blank=True, null=True)
    fg_max = BeerGravityField(verbose_name=_("FG Min"), blank=True, null=True)
    ibu_min = models.DecimalField(
        _("IBU Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    ibu_max = models.DecimalField(
        _("IBU Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    color_min = BeerColorField(verbose_name=_("Color Min"), blank=True, null=True)
    color_max = BeerColorField(verbose_name=_("Color Max"), blank=True, null=True)
    alcohol_min = models.DecimalField(
        _("Alcohol Min"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    alcohol_max = models.DecimalField(
        _("Alcohol Max"), max_digits=5, decimal_places=2, blank=True, null=True
    )
    ferm_type = models.CharField(
        _("Fermentation Type"), max_length=1000, blank=True, null=True
    )
    desc_aroma = models.TextField(_("Aroma"), max_length=1000, blank=True, null=True)
    desc_appe = models.TextField(
        _("Appearance"), max_length=1000, blank=True, null=True
    )
    desc_flavor = models.TextField(_("Flavour"), max_length=1000, blank=True, null=True)
    desc_mouth = models.TextField(
        _("Mouthfeel"), max_length=1000, blank=True, null=True
    )
    desc_overall = models.TextField(
        _("Overall"), max_length=1000, blank=True, null=True
    )
    desc_comment = models.TextField(_("Comment"), blank=True, null=True)
    desc_history = models.TextField(
        _("History"), max_length=1000, blank=True, null=True
    )
    desc_ingre = models.TextField(
        _("Ingredients"), max_length=1000, blank=True, null=True
    )
    desc_style_comp = models.TextField(
        _("Style Comparison"), max_length=1000, blank=True, null=True
    )
    commercial_exam = models.TextField(
        _("Examples"), max_length=1000, blank=True, null=True
    )
    tags = models.ManyToManyField("Tag", verbose_name=_("Tags"), blank=True, null=True)
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
            return functions.get_hex_color_from_srm(
                ((self.color_min + self.color_max) / 2.0).srm
            )
        elif self.color_min is not None:
            return functions.get_hex_color_from_srm(self.color_min.srm)
        elif self.color_max is not None:
            return functions.get_hex_color_from_srm(self.color_max.srm)
        else:
            return ""