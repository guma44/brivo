from django.core.exceptions import ValidationError
from django.forms import HiddenInput, ModelChoiceField, DateInput
from django.forms.fields import ChoiceField
from django.forms.models import ModelForm, inlineformset_factory
from django.forms import BaseInlineFormSet
from bootstrap_modal_forms.forms import BSModalModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import AppendedText, PrependedText
from crispy_forms.layout import (
    Layout,
    Hidden,
    Field,
    Fieldset,
    Div,
    HTML,
    Row,
    ButtonHolder,
    Submit,
    MultiField,
    Column)

from measurement.measures import Volume, Weight, Temperature
from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew.measurement_forms import MeasurementField
from brivo.brew import layouts
from brivo.brew import models


class MyDateInput(DateInput):
    input_type = 'date'


class PopRequestMixin:

    def get_form_kwargs(self):
        kwargs = super(PopRequestMixin, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class BaseFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(BaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(BaseFormSet, self)._construct_form(i, **kwargs)
        form.add_user_restrictions_to_field(self.request)
        return form


class BaseBatchForm(BSModalModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("l", "l"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("us_g", "us_g"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'POST'
        #self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-6 create-label'
        self.helper.field_class = 'col-md-6'
        if self.instance.stage == "INIT":
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Base Recipe Selection",
                        Field("recipe"),
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("next_stage", "Brew It!")
                    )
                )
            )
        elif self.instance.stage == "MASHING":
            if self.request.user.profile.general_units == "METRIC":
                unit_choices = (("c", "c"),)
            elif self.request.user.profile.general_units == "IMPERIAL":
                unit_choices = (("f", "f"),)
            else:
                raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
            self.fields.update({
                "grain_temperature": MeasurementField(
                    measurement=Temperature,
                    unit_choices=unit_choices),
                "sparging_temperature": MeasurementField(
                    measurement=Temperature,
                    unit_choices=unit_choices)})
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Mash",
                        Field("name"),
                        Field("batch_number"),
                        Field("brewing_day"),
                        Field("grain_temperature"),
                        Field("sparging_temperature")
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("save", "Save"),
                        Submit("next_stage", "Next")
                    )
                )
            )
        elif self.instance.stage == "BOIL":
            user_gravity_unit = self.request.user.profile.gravity_units.lower()
            self.fields.update({
                "gravity_before_boil": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=(
                        (user_gravity_unit,
                         user_gravity_unit),)),
            })

            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Boil",
                        Field("gravity_before_boil"),
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "Previous", formnovalidate='formnovalidate'),
                        Submit("save", "Save"),
                        Submit("next_stage", "Next")
                    )
                )
            )
        elif self.instance.stage == "PRIMARY_FERMENTATION":
            user_gravity_unit = self.request.user.profile.gravity_units.lower()
            if self.request.user.profile.general_units == "METRIC":
                unit_choices = (("l", "l"),)
            elif self.request.user.profile.general_units == "IMPERIAL":
                unit_choices = (("us_g", "us_g"),)
            else:
                raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
            self.fields.update({
                "initial_gravity": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=(
                        (user_gravity_unit,
                         user_gravity_unit),)),
                "wort_volume": MeasurementField(
                    measurement=Volume,
                    unit_choices=unit_choices),
            })
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Primary Fermentation",
                        Field("initial_gravity"),
                        Field("wort_volume"),
                        Field("boil_loss"),
                        Field("primary_fermentation_start_day")
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "Previous", formnovalidate='formnovalidate'),
                        Submit("save", "Save"),
                        Submit("next_stage", "Next")
                    )
                )
            )
        elif self.instance.stage == "SECONDARY_FERMENTATION":
            user_gravity_unit = self.request.user.profile.gravity_units.lower()
            self.fields.update({
                "post_primary_gravity": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=(
                        (user_gravity_unit,
                         user_gravity_unit),)),
            })
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Secondary Fermentation",
                        Field("post_primary_gravity"),
                        Field("secondary_fermentation_start_day"),
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "Previous", formnovalidate='formnovalidate'),
                        Submit("save", "Save"),
                        Submit("next_stage", "Next")
                    )
                )
            )
        elif self.instance.stage == "PACKAGING":
            user_gravity_unit = self.request.user.profile.gravity_units.lower()
            if self.request.user.profile.general_units == "METRIC":
                unit_choices = (("l", "l"),)
            elif self.request.user.profile.general_units == "IMPERIAL":
                unit_choices = (("us_g", "us_g"),)
            else:
                raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
            self.fields.update({
                "end_gravity": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=(
                        (user_gravity_unit,
                         user_gravity_unit),)),
                "beer_volume": MeasurementField(
                    measurement=Volume,
                    unit_choices=unit_choices),
            })
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Packaging",
                        Field("packaging_date"),
                        Field("end_gravity"),
                        Field("beer_volume"),
                        Field("carbonation_type"),
                        Field("carbonation_level"),
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "Previous", formnovalidate='formnovalidate'),
                        Submit("save", "Save"),
                        Submit("finish", "Finish")
                    )
                )
            )
    class Meta:
        widgets = {
                'brewing_day': MyDateInput(),
                'primary_fermentation_start_day': MyDateInput(),
                'secondary_fermentation_start_day': MyDateInput(),
                'packaging_date': MyDateInput()
            }


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


class IngredientFermentableForm(PopRequestMixin, ModelForm):

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
                unit_choices=color_choices)
        })

    class Meta:
        model = models.IngredientFermentable
        exclude = ()

IngredientFermentableFormSet = inlineformset_factory(
    models.Recipe, models.IngredientFermentable, form=IngredientFermentableForm,
    fields=['name', 'type', 'use', 'color', 'extraction', 'amount'],
    extra=1,
    can_delete=True,
    formset=BaseFormSet
)

class IngredientHopForm(PopRequestMixin, ModelForm):

    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        time_choices = (("MINUTE", "MINUTE"), ("day", "day"))
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices),
            "time_unit": ChoiceField(choices=time_choices)
        })

    class Meta:
        model = models.IngredientHop
        exclude = ()

IngredientHopFormSet = inlineformset_factory(
    models.Recipe, models.IngredientHop, form=IngredientHopForm,
    fields=['name', 'use', 'alpha_acids', 'amount', 'time', 'time_unit'], extra=1, can_delete=True, formset=BaseFormSet
)

class IngredientYeastForm(PopRequestMixin, ModelForm):

    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices),
        })

    class Meta:
        model = models.IngredientYeast
        exclude = ()

IngredientYeastFormSet = inlineformset_factory(
    models.Recipe, models.IngredientYeast, form=IngredientYeastForm,
    fields=['name', 'type', 'form', 'attenuation', 'amount', 'lab'], extra=1, can_delete=True, formset=BaseFormSet
)

class IngredientExtraForm(PopRequestMixin, ModelForm):

    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        self.fields.update({
            "amount": MeasurementField(
                measurement=Weight,
                unit_choices=unit_choices)
        })

    class Meta:
        model = models.IngredientExtra
        exclude = ()

IngredientExtraFormSet = inlineformset_factory(
    models.Recipe, models.IngredientExtra, form=IngredientExtraForm,
    fields=['name', 'type', 'use', 'amount', 'time', 'time_unit'], extra=1, can_delete=True, formset=BaseFormSet
)

class MashStepForm(PopRequestMixin, ModelForm):

    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("c", "c"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("f", "f"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
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
    fields=['temperature', 'time'], extra=1, can_delete=True, formset=BaseFormSet
)

BatchInfoStatsHtml = """
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>Boil Volume:</td>
      <td class: "text-left" id="boil_volume_info">---</td>
   <tr>
   <tr>
      <td>Pre-boil Gravity:</td>
      <td class: "text-left" id="preboil_gravity_info">---</td>
   <tr>
   <tr>
      <td>Primary Volume:</td>
      <td class: "text-left" id="primary_volume_info">---</td>
   <tr>
   <tr>
      <td>Secondary Volume:</td>
      <td class: "text-left" id="secondary_volume_info">---</td>
   <tr>
</table>
"""

FermentableInfoStatsHtml = """
<div>
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>Gravity</td>
      <td class: "text-left" id="gravity_info">---</td>
      <td class: "text-left" id="gravity_styleinfo">---</td>
   <tr>
   <tr>
      <td>Expected ABV</td>
      <td class: "text-left" id="abv_info">---</td>
      <td class: "text-left" id="abv_styleinfo">---</td>
   <tr>
   <tr>
      <td>Color</td>
      <td class: "text-left" id="color_info">---</td>
      <td class: "text-left" id="color_styleinfo">---</td>
   <tr>
</table>
</div>
"""

HopInfoStatsHtml = """
<div>
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>Bitterness</td>
      <td class: "text-left" id="ibu_info">---</td>
      <td class: "text-left" id="ibu_styleinfo">---</td>
   <tr>
   <tr>
      <td>Bitterness Ratio</td>
      <td class: "text-left" id="bitterness_ratio_info">---</td>
      <td class: "text-left" id="bitterness_ratio_name_info">---</td>
   <tr>
</table>
</div>
"""

class RecipeModelForm(BSModalModelForm):

    def __init__(self, *args, **kwargs):
        super(RecipeModelForm, self).__init__(*args, **kwargs)
        if self.request.user.profile.general_units == "METRIC":
            unit_choices = (("l", "l"),)
        elif self.request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("us_g", "us_g"),)
        else:
            raise ValueError(f"No unit choice {self.request.user.profile.general_units}")
        self.fields.update({
            "expected_beer_volume": MeasurementField(
                measurement=Volume,
                unit_choices=unit_choices),
        })

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_method = 'POST'
        #self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-6 create-label'
        self.helper.field_class = 'col-md-6'
        self.helper.layout = Layout(
            Div(
                Fieldset("Recipe Information", Field("type"), Field("name"), Field("style")),
                Fieldset("Batch Information",
                    Row(
                        Column(Field("expected_beer_volume"), css_class='form-group col-md-6 mb-0'),
                        css_class="form-row"),
                    Row(
                        Column(AppendedText("boil_time", "min"), css_class='form-group col-md-4 mb-0'),
                        Column(AppendedText("evaporation_rate", "%/h"), css_class='form-group col-md-4 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        Column(AppendedText("boil_loss", "%"), css_class='form-group col-md-4 mb-0'),
                        Column(AppendedText("trub_loss", "%"), css_class='form-group col-md-4 mb-0'),
                        Column(AppendedText("dry_hopping_loss", "%"), css_class='form-group col-md-4 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        Column(HTML(BatchInfoStatsHtml), css_class='form-group col-md-3 mb-0'),
                        css_class='form-row'
                    )
                ),
                Fieldset('Fermentables',
                    Row(
                        Column(HTML(FermentableInfoStatsHtml), css_class='form-group col-md-4 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        layouts.RecipeFormsetLayout('fermentables', "brew/recipe/fermentable_formset.html"),
                        css_class="form-row"
                    ),
                ),
                Fieldset(
                    "Mash",
                    Row(
                        Column(AppendedText("mash_efficiency", "%"), css_class='form-group col-md-4 mb-0'),
                        Column(AppendedText("liquor_to_grist_ratio", "?"), css_class='form-group col-md-4 mb-0'),
                        css_class="form-row"
                    ),
                    Row(
                        layouts.RecipeFormsetLayout('mash_steps', "brew/recipe/mash_formset.html"),
                        css_class="form-row"
                    )
                ),
                Fieldset("Hops",
                    Row(
                        Column(HTML(HopInfoStatsHtml), css_class='form-group col-md-4 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        layouts.RecipeFormsetLayout('hops', "brew/recipe/hop_formset.html"),
                        css_class="form-row"
                    ),
                ),
                Fieldset("Yeasts", layouts.RecipeFormsetLayout('yeasts', "brew/recipe/yeast_formset.html")),
                Field('note'),
                HTML("<br>")
            ),
        )


    class Meta:
        model = models.Recipe
        exclude = ['user', ]