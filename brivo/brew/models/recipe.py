from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


from brivo.brew.models import BaseModel, VOLUME_UNITS
from brivo.utils import functions
from brivo.utils.measures import BeerColor, BeerGravity

from django_measurement.models import MeasurementField
from measurement.measures import Volume, Weight


__all__ = ("RecipeCalculatorMixin", "Recipe")


RECIPE_TYPE = [
    ("ALL GRAIN", "All Grain"),
    ("EXTRACT", "Extract"),
    ("PARTIAL MASH", "Partial Mash"),
]


class RecipeCalculatorMixin:
    """Mixin used in Recipe model and recipe ajax call."""

    def get_boil_loss_volume(self):
        return self.expected_beer_volume * (float(self.boil_loss) / 100.0)

    def get_trub_loss_volume(self):
        return self.expected_beer_volume * (float(self.trub_loss) / 100.0)

    def get_dry_hopping_loss_volume(self):
        return self.expected_beer_volume * (float(self.dry_hopping_loss) / 100.0)

    def get_initial_volume(self):
        boil_loss = self.get_boil_loss_volume()
        trub_loss = self.get_trub_loss_volume()
        dry_hopping_loss = self.get_dry_hopping_loss_volume()
        volume = self.expected_beer_volume + boil_loss + trub_loss + dry_hopping_loss
        return volume

    def get_boil_volume(self):
        initial_volume = self.get_initial_volume()
        volume = initial_volume + (
            initial_volume * (float(self.evaporation_rate) / 100.0)
        )
        return volume

    def get_preboil_gravity(self):
        eff = float(self.mash_efficiency)
        grain_sugars = self.get_grain_sugars().kg * eff
        other_sugars = self.get_other_sugars().kg * 100.0
        grain_gravity = grain_sugars / (
            self.get_boil_volume().l - grain_sugars / 145.0 + grain_sugars / 100.0
        )
        other_gravity = other_sugars / (
            self.get_boil_volume().l - other_sugars / 145.0 + other_sugars / 100.0
        )
        # print(f"{self.name} [{self.get_boil_volume().l}] - Grain gravity: {grain_gravity}, Other gravity: {other_gravity}, {eff}")
        return BeerGravity(plato=(grain_gravity + other_gravity))

    def get_primary_volume(self):
        volume = self.expected_beer_volume.l
        trub_loss = volume * (float(self.trub_loss) / 100.0)
        dry_hopping_loss = volume * (float(self.dry_hopping_loss) / 100.0)
        volume = volume + trub_loss + dry_hopping_loss
        return Volume(l=volume)

    def get_secondary_volume(self):
        volume = self.expected_beer_volume.l
        dry_hopping_loss = volume * (float(self.dry_hopping_loss) / 100.0)
        volume = volume + dry_hopping_loss
        return Volume(l=volume)

    def get_color(self):
        added_colors = []
        for fermentable in self.get_fermentables():
            if fermentable.color.srm > 0 and fermentable.amount.kg > 0:
                added_colors.append(
                    functions.calculate_mcu(
                        color=fermentable.color.srm,
                        weigth=fermentable.amount.kg,
                        volume=self.expected_beer_volume.l,
                    )
                )
        return BeerColor(srm=functions.morey_equation(sum(added_colors)))

    def get_hex_color(self):
        return functions.get_hex_color_from_srm(self.get_color().srm)

    def get_volume_unit(self):
        if self.user.profile.general_units.lower() == "metric":
            return "l"
        else:
            return "us_g"

    def get_max_attenuation(self):
        min_val = 101
        for yeast in self.get_yeasts():
            if yeast.attenuation < min_val:
                min_val = yeast.attenuation
        if min_val > 100:
            min_val = 75.0
        return float(min_val) / 100

    def get_final_gravity(self):
        return self.get_gravity().plato * (1 - self.get_max_attenuation())

    def get_abv(self):
        return (self.get_gravity().plato - self.get_final_gravity()) * 0.516

    def get_fermentable_sugar(self, fermentable):
        sugar = fermentable.amount.kg * float(fermentable.extraction) / 100.0
        return Weight(kg=sugar)

    def get_grain_sugars(self):
        sugars = Weight(kg=0.0)
        for fermentable in self.get_fermentables():
            if fermentable.type != "GRAIN":
                continue
            sugars += self.get_fermentable_sugar(fermentable)
        return Weight(kg=sugars.kg)

    def get_other_sugars(self):
        sugars = Weight(kg=0.0)
        for fermentable in self.get_fermentables():
            if fermentable.type == "GRAIN":
                continue
            sugars += self.get_fermentable_sugar(fermentable)
        return Weight(kg=sugars.kg)

    def get_gravity(self):
        eff = float(self.mash_efficiency)
        grain_sugars = self.get_grain_sugars().kg * eff
        other_sugars = self.get_other_sugars().kg * 100.0
        grain_gravity = grain_sugars / (
            self.get_initial_volume().l - grain_sugars / 145.0 + grain_sugars / 100.0
        )
        other_gravity = other_sugars / (
            self.get_initial_volume().l - other_sugars / 145.0 + other_sugars / 100.0
        )
        # print(f"{self.name} [{self.get_initial_volume().l}] - Grain gravity: {grain_gravity}, Other gravity: {other_gravity}, {eff}")
        return BeerGravity(plato=(grain_gravity + other_gravity))

    def get_ibu(self):
        added_ibus = []
        for hop in self.get_hops():
            if hop.use in ["BOIL", "AROMA", "FIRST WORT", "WHIRLPOOL"]:
                if hop.amount.g > 0 and hop.time > 0 and hop.alpha_acids > 0:
                    added_ibus.append(
                        functions.calculate_ibu_tinseth(
                            og=self.get_gravity().sg,
                            time=float(hop.time),
                            type="PELLETS",
                            alpha=float(hop.alpha_acids),
                            weight=hop.amount.g,
                            volume=self.get_initial_volume().l,
                        )
                    )
        return sum(added_ibus)

    def get_bitterness_ratio(self):
        return self.get_ibu() / ((float(self.get_gravity().sg) - 1) * 1e3)

    def get_mash_size(self):
        pass

    def get_total_mash_volume(self):
        pass


class Recipe(RecipeCalculatorMixin, BaseModel):
    user = models.ForeignKey("users.User", verbose_name=_("User"), on_delete=models.CASCADE)
    # Recipe info
    style = models.ForeignKey(
        "Style", verbose_name=_("Style"), on_delete=models.DO_NOTHING
    )
    type = models.CharField(_("Type"), max_length=1000, choices=RECIPE_TYPE)

    # Batch info
    expected_beer_volume = MeasurementField(
        measurement=Volume,
        verbose_name=_("Expected Beer Volume"),
        unit_choices=VOLUME_UNITS,
        default=20
    )
    boil_time = models.IntegerField(_("Boil Time"), default=60.0)
    evaporation_rate = models.DecimalField(
        _("Evaporation Rate"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=10.0,
    )
    boil_loss = models.DecimalField(
        _("Boil Loss"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=10.0,
    )
    trub_loss = models.DecimalField(
        _("Trub Loss"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=5.0,
    )
    dry_hopping_loss = models.DecimalField(
        _("Dry Hopping Loss"),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0,
    )
    # Mashing
    mash_efficiency = models.DecimalField(
        _("Mash Efficiency"), max_digits=5, decimal_places=2, default=75.0
    )
    liquor_to_grist_ratio = models.DecimalField(
        _("Liquor-To-Grist Ratio"), max_digits=5, decimal_places=2, default=3.0
    )
    # Rest
    note = models.TextField(_("Note"), max_length=1000, blank=True)
    is_public = models.BooleanField(_("Public"), default=True)

    def get_fermentables(self):
        return self.fermentables.all()

    def get_yeasts(self):
        return self.yeasts.all()

    def get_hops(self):
        return self.hops.all()

    def __str__(self):
        return f"{self.pk}. {self.name}"
