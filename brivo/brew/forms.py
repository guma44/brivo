from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.forms.models import ModelForm
from bootstrap_modal_forms.forms import BSModalModelForm
from django_measurement.forms import MeasurementField
from measurement.measures import Volume, Weight, Temperature

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew.models import Fermentable, Hop


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
        print(self.request.user)
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