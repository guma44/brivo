import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _


from brivo.brewery.models import BaseModel, VOLUME_UNITS
from brivo.utils.measures import BeerGravity
from brivo.brewery.fields import TemperatureField, BeerGravityField, VolumeField
from brivo.utils import functions

from modelcluster.fields import ParentalKey


__all__ = ("Batch", "FermentationCheck", "BATCH_STAGE_ORDER", "BATCH_STAGES", "SUGAR_TYPE")


BATCH_STAGES = (
    ("INIT", _("Init")),
    ("MASHING", _("Mashing")),
    ("BOIL", _("Boil")),
    ("PRIMARY_FERMENTATION", _("Primary Fermentation")),
    ("SECONDARY_FERMENTATION", _("Secondary Fermentation")),
    ("PACKAGING", _("Packaging")),
    ("FINISHED", _("Finished")),
)

BATCH_STAGE_ORDER = [bs[0] for bs in BATCH_STAGES]

CARBONATION_TYPE = (("FORCED", _("Forced")), ("REFERMENTATION", _("Refermentation")))
SUGAR_TYPE = (
    ("CORN_SUGAR", _("Corn Sugar")),
    ("TABLE_SUGAR", _("Table Sugar")),
    ("DRY_EXTRACT", _("Dry Extract"))
)

class FermentationCheck(BaseModel):
    batch = ParentalKey(
        "brewery.Batch",
        verbose_name=_("Batch"),
        on_delete=models.CASCADE,
        related_name="fermentation_checks",
    )
    sample_day = models.DateField(
        _("Sample Day"),
        null=True,
        auto_now=False,
        auto_now_add=False,
    )
    gravity = BeerGravityField(
        verbose_name=_("Gravity"), null=True
    )
    beer_temperature = TemperatureField(
        verbose_name=_("Beer Temperature"), null=True, blank=True
    )
    ambient_temperature = TemperatureField(
        verbose_name=_("Ambient Temperature"), null=True, blank=True
    )
    comment = models.TextField(_("Comment"), blank=True, null=True)


class Batch(BaseModel):
    # Operational fields
    stage = models.CharField(
        _("Stage"), max_length=50, choices=BATCH_STAGES, default="INIT"
    )
    recipe = ParentalKey("Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE)
    user = models.ForeignKey(
        "users.User", verbose_name=_("User"), on_delete=models.CASCADE
    )

    # Stage 1 fields: info and mashing
    # name - inherited from BaseModel
    batch_number = models.IntegerField(_("Batch Number"), null=True)
    brewing_day = models.DateField(
        _("Brewing Day"), auto_now=False, auto_now_add=False, null=True
    )
    grain_temperature = TemperatureField(
        verbose_name=_("Grain Temperature"), null=True, default=273.15 + 20
    )
    sparging_temperature = TemperatureField(
        verbose_name=_("Sparging Temperature"), null=True, default=273.15 + 78
    )

    # Stage 2 fields: boil
    gravity_before_boil = BeerGravityField(
        verbose_name=_("Gravity Before Boil"), null=True
    )

    # Stage 3 fields: primary fermentation
    initial_gravity = BeerGravityField(verbose_name=_("Initial Gravity"), null=True)
    wort_volume = VolumeField(
        verbose_name=_("Wort Volume"),
        null=True,
        unit_choices=VOLUME_UNITS,
    )
    boil_loss = VolumeField(
        verbose_name=_("Boil Waists"),
        null=True,
        unit_choices=VOLUME_UNITS,
    )
    primary_fermentation_temperature = TemperatureField(
        verbose_name=_("Primary Fermentation Temperature"), null=True, blank=True
    )
    primary_fermentation_start_day = models.DateField(
        _("Primary Fermentation Start Day"),
        null=True,
        auto_now=False,
        auto_now_add=False,
    )

    # Stage 4 fields: secondary fermentation
    secondary_fermentation_temperature = TemperatureField(
        verbose_name=_("Secondary Fermentation Temperature"), null=True, blank=True
    )
    secondary_fermentation_start_day = models.DateField(
        _("Secondary Fermentation Start Day"),
        null=True,
        blank=True,
        auto_now=False,
        auto_now_add=False,
    )
    dry_hops_start_day = models.DateField(
        _("Dry Hops Start Day"),
        null=True,
        blank=True,
        auto_now=False,
        auto_now_add=False,
    )
    post_primary_gravity = BeerGravityField(
        verbose_name=_("Post-primary Gravity"),
        null=True,
        blank=True,
    )

    # Stage 4 fields: packaging
    packaging_date = models.DateField(
        _("Packaging Start Day"), auto_now=False, auto_now_add=False, null=True
    )
    end_gravity = BeerGravityField(verbose_name=_("End Gravity"), null=True)
    beer_volume = VolumeField(
        verbose_name=_("Beer Volume"),
        null=True,
        unit_choices=VOLUME_UNITS,
    )
    carbonation_type = models.CharField(
        _("Carbonation Type"), max_length=50, choices=CARBONATION_TYPE, null=True
    )
    carbonation_level = models.DecimalField(
        _("Carbonation Level"), max_digits=5, decimal_places=2, null=True
    )
    sugar_type = models.CharField(
        _("Sugar Type"), max_length=50, choices=SUGAR_TYPE, null=True, blank=True
    )
    priming_temperature = TemperatureField(
        verbose_name=_("Priming Temperature"), null=True, blank=True
    )

    hidden_fields = ["stage"]

    def get_hex_color(self):
        return self.recipe.get_hex_color()

    def get_size_with_trub_loss(self):
        pass

    def get_actuall_mash_efficiency(self):
        try:
            vol = self.wort_volume.l + self.boil_loss.l
            grain_sugars = self.recipe.get_grain_sugars().kg * 100.0
            other_sugars = self.recipe.get_other_sugars().kg * 100.0
            grain_gravity = grain_sugars / (
                vol - grain_sugars / 145.0 + grain_sugars / 100.0
            )
            other_gravity = other_sugars / (
                vol - other_sugars / 145.0 + other_sugars / 100.0
            )
            max_gravity = BeerGravity(plato=(grain_gravity + other_gravity))
            return (
                (self.initial_gravity.plato * vol)
                / (max_gravity.plato * self.recipe.get_primary_volume().l)
            ) * 100.0
        except AttributeError:
            return None

    def get_ibu(self):
        added_ibus = []
        try:
            for hop in self.recipe.hops.all():
                if hop.use in ["BOIL", "AROMA", "FIRST WORT", "WHIRLPOOL"]:
                    if hop.amount.g > 0 and hop.time > 0 and hop.alpha_acids > 0:
                        added_ibus.append(
                            functions.calculate_ibu_tinseth(
                                og=self.initial_gravity.sg,
                                time=float(hop.time),
                                type="PELLETS",
                                alpha=float(hop.alpha_acids),
                                weight=hop.amount.g,
                                volume=self.wort_volume.l + self.boil_loss.l,
                            )
                        )
        except AttributeError:
            return None
        return sum(added_ibus)

    def get_abv(self):
        try:
            return functions.get_abv(self.initial_gravity.sg, self.end_gravity.sg)
        except AttributeError:
            return None

    def get_attenuation(self):
        try:
            return functions.get_attenuation(self.initial_gravity.sg, self.end_gravity.sg)
        except AttributeError:
            return None

    def get_calories(self):
        try:
            return functions.get_beer_calories(self.initial_gravity.sg, self.end_gravity.sg)
        except AttributeError:
            return None

    @staticmethod
    def get_fields_by_stage(stage):
        fields = ["stage"]  # Must always be present
        if stage == "INIT":
            fields.extend(["recipe"])
        elif stage == "MASHING":
            fields.extend(
                [
                    "name",
                    "batch_number",
                    "brewing_day",
                    "grain_temperature",
                    "sparging_temperature",
                ]
            )
        elif stage == "BOIL":
            fields.extend(["gravity_before_boil"])
        elif stage == "PRIMARY_FERMENTATION":
            fields.extend(
                [
                    "initial_gravity",
                    "wort_volume",
                    "boil_loss",
                    "primary_fermentation_temperature",
                    "primary_fermentation_start_day",
                ]
            )
        elif stage == "SECONDARY_FERMENTATION":
            fields.extend(
                [
                    "post_primary_gravity",
                    "secondary_fermentation_start_day",
                    "dry_hops_start_day",
                ]
            )
        elif stage == "PACKAGING":
            fields.extend(
                [
                    "packaging_date",
                    "end_gravity",
                    "beer_volume",
                    "carbonation_type",
                    "carbonation_level",
                    "sugar_type",
                    "priming_temperature"
                ]
            )
        return fields

    def get_ndays_since_brewing(self):
        today = datetime.datetime.now().date()
        if self.primary_fermentation_start_day is not None:
            ndays = (today - self.primary_fermentation_start_day).days
            return ndays
        else:
            return 0
        