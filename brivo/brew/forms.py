from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.forms.models import ModelForm
from bootstrap_modal_forms.forms import BSModalModelForm
from django_measurement.forms import MeasurementField
from measurement.measures import Volume, Weight, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew.models import Fermentable, Hop, Yeast, Extra, Style


class BaseBatchForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = self.instance.required_fields
        hidden_fields = self.instance.hidden_fields
        for field in self.fields:
            if field in required_fields:
                self.fields.get(field).required = True
            if field in hidden_fields:
                self.fields.get(field).widget = HiddenInput()


class FermentableModelForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(FermentableModelForm, self).__init__(*args, **kwargs)
        self.fields.update({
            "color": MeasurementField(
                measurement=BeerColor,
                unit_choices=(
                    (self.request.user.profile.color_units.lower(),
                    self.request.user.profile.color_units.lower()),))})

    class Meta:
        model = Fermentable
        fields = "__all__"


class HopModelForm(BSModalModelForm):

    class Meta:
        model = Hop
        fields = "__all__"


class YeastModelForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(YeastModelForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("c", "c"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("f", "f"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        self.fields.update({
            "temp_min": MeasurementField(
                measurement=Temperature,
                unit_choices=unit_choices),
            "temp_max": MeasurementField(
                measurement=Temperature,
                unit_choices=unit_choices)})

    class Meta:
        model = Yeast
        fields = "__all__"


class ExtraModelForm(BSModalModelForm):

    class Meta:
        model = Extra
        fields = "__all__"


class StyleModelForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(StyleModelForm, self).__init__(*args, **kwargs)
        user_color_unit = self.request.user.profile.color_units.lower()
        user_gravity_unit = self.request.user.profile.gravity_units.lower()
        self.fields.update({
            "color_min": MeasurementField(
                measurement=BeerColor,
                unit_choices=(
                    (user_color_unit,
                     user_color_unit),)),
            "color_max": MeasurementField(
                measurement=BeerColor,
                unit_choices=(
                    (user_color_unit,
                     user_color_unit),)),
            "og_min": MeasurementField(
                measurement=BeerGravity,
                unit_choices=(
                    (user_gravity_unit,
                     user_gravity_unit),)),
            "og_max": MeasurementField(
                measurement=BeerGravity,
                unit_choices=(
                    (user_gravity_unit,
                     user_gravity_unit),)),
            "fg_min": MeasurementField(
                measurement=BeerGravity,
                unit_choices=(
                    (user_gravity_unit,
                     user_gravity_unit),)),
            "fg_max": MeasurementField(
                measurement=BeerGravity,
                unit_choices=(
                    (user_gravity_unit,
                     user_gravity_unit),)),
        })

    class Meta:
        model = Style
        fields = "__all__"
