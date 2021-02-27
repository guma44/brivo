from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.forms.fields import ChoiceField
from django.forms.models import ModelForm, inlineformset_factory
from django.forms import BaseInlineFormSet
from bootstrap_modal_forms.forms import BSModalModelForm
from django_measurement.forms import MeasurementField
from measurement.measures import Volume, Weight, Temperature
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit

from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew import layouts
from brivo.brew import models


class BaseFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(BaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(BaseFormSet, self)._construct_form(i, **kwargs)
        form.add_user_restrictions_to_field(self.request)
        return form


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
        model = models.Fermentable
        fields = "__all__"


class HopModelForm(BSModalModelForm):

    class Meta:
        model = models.Hop
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
        model = models.Yeast
        fields = "__all__"


class ExtraModelForm(BSModalModelForm):

    class Meta:
        model = models.Extra
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
        model = models.Style
        fields = "__all__"


class FermentableIngredientForm(BSModalModelForm):

    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("kg", "kg"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("lb", "lb"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        user_color_unit = request.user.profile.color_units.lower()
        color_choices = ((user_color_unit, user_color_unit),)
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices),
            "color": MeasurementField(
                measurement=BeerColor,
                unit_choices=unit_choices)
        })

    class Meta:
        model = models.FermentableIngredient
        exclude = ()

FermentableIngredientFormSet = inlineformset_factory(
    models.Recipe, models.FermentableIngredient, form=FermentableIngredientForm,
    fields=['name', 'type', 'use', 'color', 'extraction', 'amount'],
    extra=1,
    can_delete=True,
    formset=BaseFormSet
)

class HopIngredientForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(HopIngredientForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        time_choices = (("min", "min"), ("day", "day"))
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices),
            "time_unit": forms.ChoiceField("Unit", choices=time_choices, required=True)
        })

    class Meta:
        model = models.HopIngredient
        exclude = ()

HopIngredientFormSet = inlineformset_factory(
    models.Recipe, models.HopIngredient, form=HopIngredientForm,
    fields=['name', 'use', 'alpha_acids', 'amount', 'time', 'time_unit'], extra=1, can_delete=True
)

class YeastIngredientForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(YeastIngredientForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices),
        })

    class Meta:
        model = models.YeastIngredient
        exclude = ()

YeastIngredientFormSet = inlineformset_factory(
    models.Recipe, models.YeastIngredient, form=YeastIngredientForm,
    fields=['name', 'type', 'form', 'attenuation', 'amount', 'lab'], extra=1, can_delete=True
)

class ExtraIngredientForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(ExtraIngredientForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices)
        })

    class Meta:
        model = models.ExtraIngredient
        exclude = ()

ExtraIngredientFormSet = inlineformset_factory(
    models.Recipe, models.ExtraIngredient, form=ExtraIngredientForm,
    fields=['name', 'type', 'use', 'amount', 'time', 'time_unit'], extra=1, can_delete=True
)

class MashStepForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(MashStepForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("c", "c"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("f", "f"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        self.fields.update({
            "temperature": MeasurementField(
                measurement=Temperature,
                unit_choices=unit_choices),
        })

    class Meta:
        model = models.MashStep
        exclude = ()

MashStepFormSet = inlineformset_factory(
    models.Recipe, models.MashStep, form=MashStepForm,
    fields=['temperature', 'time'], extra=1, can_delete=True
)


class RecipeModelForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(RecipeModelForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("l", "l"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("US Gal", "US Gal"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        self.fields.update({
            "expected_beer_volume": MeasurementField(
                measurement=Temperature,
                unit_choices=unit_choices),
        })

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(
                Field('style'),
                Fieldset('Add Fermentables',
                    layouts.RecipeFormsetLayout('fermentables')),
                Field('note'),
                HTML("<br>"),
                ButtonHolder(Submit('submit', 'save')),
                )
            )


    class Meta:
        model = models.Recipe
        exclude = ['user', ]