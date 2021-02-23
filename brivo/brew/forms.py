from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.forms.models import ModelForm
from bootstrap_modal_forms.forms import BSModalModelForm
from django_measurement.forms import MeasurementField
from measurement.measures import Volume, Weight, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew.models import Fermentable, Hop, Yeast


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