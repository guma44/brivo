from django.db import models
from django.utils.translation import gettext_lazy as _


from brivo.brew.models import BaseModel, VOLUME_UNITS
from brivo.utils.measures import BeerGravity

from django_measurement.models import MeasurementField
from measurement.measures import Volume, Temperature


__all__ = ("Batch", "BATCH_STAGE_ORDER", "BATCH_STAGES")


BATCH_STAGES = (
    ("INIT", "Init"),
    ("MASHING", "Mashing"),
    ("BOIL", "Boil"),
    ("PRIMARY_FERMENTATION", "Primary Fermentation"),
    ("SECONDARY_FERMENTATION", "Secondary Fermentation"),
    ("PACKAGING", "Packaging"),
    ("FINISHED", "Finished"),
)

BATCH_STAGE_ORDER = [bs[0] for bs in BATCH_STAGES]

CARBONATION_TYPE = (("FORCED", "Forced"), ("REFERMENTATION", "Refermentation"))


class Batch(BaseModel):
    # Operational fields
    stage = models.CharField(
        _("Stage"), max_length=50, choices=BATCH_STAGES, default="INIT"
    )
    recipe = models.ForeignKey(
        "Recipe", verbose_name=_("Recipe"), on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "users.User", verbose_name=_("User"), on_delete=models.CASCADE
    )

    # Stage 1 fields: info and mashing
    # name - inherited from BaseModel
    batch_number = models.IntegerField(_("Batch Number"), null=True)
    brewing_day = models.DateField(
        _("Brewing Day"), auto_now=False, auto_now_add=False, null=True
    )
    grain_temperature = MeasurementField(
        measurement=Temperature, verbose_name=_("Grain Temperature"), null=True, default=Temperature(c=20)
    )
    sparging_temperature = MeasurementField(
        measurement=Temperature, verbose_name=_("Sparging Temperature"), null=True, default=Temperature(c=78)
    )

    # Stage 2 fields: boil
    gravity_before_boil = MeasurementField(
        measurement=BeerGravity, verbose_name=_("Gravity Before Boil"), null=True
    )

    # Stage 3 fields: primary fermentation
    initial_gravity = MeasurementField(
        measurement=BeerGravity, verbose_name=_("Initial Gravity"), null=True
    )
    wort_volume = MeasurementField(
        measurement=Volume,
        verbose_name=_("Wort Volume"),
        null=True,
        unit_choices=VOLUME_UNITS,
    )
    boil_loss = models.DecimalField(
        _("Boil Waists"), max_digits=5, decimal_places=2, null=True
    )
    primary_fermentation_start_day = models.DateField(
        _("Primary Fermentation Start Day"),
        null=True,
        auto_now=False,
        auto_now_add=False,
    )

    # Stage 4 fields: secondary fermentation
    secondary_fermentation_start_day = models.DateField(
        _("Secondary Fermentation Start Day"),
        null=True,
        auto_now=False,
        auto_now_add=False,
    )
    dry_hops_start_day = models.DateField(
        _("Dry Hops Start Day"), null=True, auto_now=False, auto_now_add=False
    )
    post_primary_gravity = MeasurementField(
        measurement=BeerGravity, verbose_name=_("Post-primary Gravity"), null=True
    )

    # Stage 4 fields: packaging
    packaging_date = models.DateField(
        _("Packaging Start Day"), auto_now=False, auto_now_add=False, null=True
    )
    end_gravity = MeasurementField(
        measurement=BeerGravity, verbose_name=_("End Gravity"), null=True
    )
    beer_volume = MeasurementField(
        measurement=Volume,
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

    hidden_fields = ["stage"]

    def get_hex_color(self):
        return self.recipe.get_hex_color()

    def get_expected_gravity(self):
        pass

    def get_size_with_trub_loss(self):
        pass

    def get_estimated_boil_loss(self):
        pass

    def get_actuall_mash_efficiency(self):
        pass

    def get_batch_bitterness(self):
        pass

    def get_abv(self):
        pass

    def get_attenuation(self):
        pass

    def get_calories(self):
        pass

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
                    "primary_fermentation_start_day",
                ]
            )
        elif stage == "SECONDARY_FERMENTATION":
            fields.extend(["post_primary_gravity", "secondary_fermentation_start_day"])
        elif stage == "PACKAGING":
            fields.extend(
                [
                    "packaging_date",
                    "end_gravity",
                    "beer_volume",
                    "carbonation_type",
                    "carbonation_level",
                ]
            )
        return fields