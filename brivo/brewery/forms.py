from django.core.exceptions import ValidationError
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from django.forms import HiddenInput, ModelChoiceField
from django.forms.fields import ChoiceField, FileField, IntegerField
from django.forms.models import ModelForm, inlineformset_factory
from django.forms import BaseInlineFormSet, Form
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
from brivo.brewery.measurement_forms import MeasurementField
from brivo.brewery import layouts
from brivo.brewery import models

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


mash_info_for_batch = """
{% load brew_tags %}
<div class="mashing mt-5 mb-5">
    <h5>Mash information</h5>
    <table class="table table-sm">
    <tbody>
        <tr>
        <th>Boil size</th>
        <td>{{batch.recipe.get_boil_volume|get_obj_attr:volume.0|floatformat}} {{volume.1}}</td>
        <tr>
        <tr>
        <th>Mash Efficiency</th>
        <td>{{batch.recipe.mash_efficiency|floatformat}}%</td>
        <tr>
        <tr>
        <th>Liquor-to-Grist Ratio</th>
        <td>{{batch.recipe.liquor_to_grist_ratio|floatformat}} {{volume.1}}/{{big_weight.1}}</td>
        <tr>
    </tbody>
    </table>
</div>
<div class="ingredients mt-5 mb-5">
    <h5>Fermentables</h5>
    <table class="table table-sm">
        <thead>
            <tr>
                <th class="text-left" scope="col">Name</th>
                <th class="text-left" scope="col">Type</th>
                <th class="text-left" scope="col">Use</th>
                <th class="text-left" scope="col">Color</th>
                <th class="text-left" scope="col">Extraction</th>
                <th class="text-left" scope="col">Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for fermentable in batch.recipe.fermentables.all %}
                <tr class="">
                    <td class="text-left">{{ fermentable.name }}</td>
                    <td class="text-left">{{ fermentable.type|title }}</td>
                    <td class="text-left">{{ fermentable.use|title|default:"---" }}</td>
                    <td class="text-left">{{ fermentable.color|get_obj_attr:color_units.0|floatformat }} {{color_units.1}}</td>
                    <td class="text-left">{{ fermentable.extraction }}%</td>
                    <td class="text-left">{{ fermentable.amount|get_obj_attr:big_weight.0|floatformat }} {{big_weight.1}}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
"""

boil_info_for_batch = """
{% load brew_tags %}
<div class="ingredients mt-5 mb-5">
    <h5>Hops</h5>
    <table class="table table-sm">
        <thead>
            <tr >
                <th class="text-left" scope="col">Name</th>
                <th class="text-left" scope="col">Use</th>
                <th class="text-left" scope="col">Alpha Acids</th>
                <th class="text-left" scope="col">Amount</th>
                <th class="text-left" scope="col">Time</th>
            </tr>
        </thead>
        <tbody>
            {% for hop in batch.recipe.hops.all %}
                {% if hop.use != "DRY HOP" %}
                <tr>
                    <td class="text-left">{{ hop.name }}</td>
                    <td class="text-left">{{ hop.use|title }}</td>
                    <td class="text-left">{{ hop.alpha_acids }}%</td>
                    <td class="text-left">{{ hop.amount|get_obj_attr:small_weight.0 }} {{small_weight.1}}</td>
                    <td class="text-left">{{ hop.time|floatformat }} {{hop.time_unit|lower}}(s)</td>
                </tr>
                {% endif %}
            {% endfor %}
        </tbody>
    </table>
</div>
"""

boil_stats_for_batch = """
{% load brew_tags %}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>Expected Boil Volume:</td>
      <td class: "text-left" id="expected_boil_volume_info">{{ batch.recipe.get_boil_volume|get_obj_attr:volume.0|floatformat }}  {{volume.1}}</td>
   <tr>
   <tr>
      <td>Expected Pre-Boil Gravity:</td>
      <td class: "text-left" id="expected_preboil_gravity_info">{{ batch.recipe.get_preboil_gravity|get_obj_attr:gravity_units.0|floatformat}} {{gravity_units.1}}</td>
   <tr>
   <tr>
      <td>Boil Time:</td>
      <td class: "text-left" id="primary_volume_info">{{ batch.recipe.boil_time }} Min</td>
   <tr>
</table>
"""

primary_info_for_batch = """
{% load brew_tags %}
<div class="ingredients mt-5 mb-5">
    <h5>Yeasts</h5>
    <table class="table table-sm">
        <thead>
            <tr >
                <th class="text-left" scope="col">Name</th>
                <th class="text-left" scope="col">Lab</th>
                <th class="text-left" scope="col">Type</th>
                <th class="text-left" scope="col">Attenuation</th>
                <th class="text-left" scope="col">Form</th>
                <th class="text-left" scope="col">Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for yeast in batch.recipe.yeasts.all %}
                <tr>
                    <td class="text-left">{{ yeast.name }}</td>
                    <td class="text-left">{{ yeast.lab }}</td>
                    <td class="text-left">{{ yeast.type|title }}</td>
                    <td class="text-left">{{ yeast.attenuation|floatformat }}%</td>
                    <td class="text-left">{{ yeast.form|title }}</td>
                    <td class="text-left">{{ yeast.amount|get_obj_attr:small_weight.0|floatformat }} {{small_weight.1}}</td>
                </tr>
            {% endfor %}
    </table>
</div>
"""

primary_stats_for_batch = """
{% load brew_tags %}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>Expected Gravity:</td>
      <td class: "text-left" id="expected_gravity_info">{{ batch.recipe.get_gravity|get_obj_attr:gravity_units.0|floatformat}} {{gravity_units.1}}</td>
   <tr>
   <tr>
      <td>Expected Volume With Trub Loss:</td>
      <td class: "text-left" id="expected_boil_volume_with_trub_loss_info">{{ batch.recipe.get_primary_volume|get_obj_attr:volume.0|floatformat }}  {{volume.1}}</td>
   <tr>
   <tr>
      <td>Expected Boil Loss:</td>
      <td class: "text-left" id="expected_boil_loss_info">{{ batch.recipe.get_boil_loss_volume|get_obj_attr:volume.0|floatformat }}  {{volume.1}}</td>
   <tr>
   <tr>
      <td>Batch IBU:</td>
      <td class: "text-left" id="primary_volume_info">{{ batch.get_ibu|floatformat|default:"---" }}</td>
   <tr>
   <tr>
      <td>Actual Mash Efficiency:</td>
      <td class: "text-left" id="actual_mash_efficiency_info">{{ batch.get_actuall_mash_efficiency|floatformat|default:"---" }}%</td>
   <tr>
</table>
"""

secondary_info_for_batch = """
{% load brew_tags %}
<div class="ingredients mt-5 mb-5">
    {% if batch.recipe.hops.all|count_dry_hops > 0 %}
    <h5>Hops</h5>
    <table class="table table-sm">
        <thead>
            <tr >
                <th class="text-left" scope="col">Name</th>
                <th class="text-left" scope="col">Use</th>
                <th class="text-left" scope="col">Alpha Acids</th>
                <th class="text-left" scope="col">Amount</th>
                <th class="text-left" scope="col">Time</th>
            </tr>
        </thead>
        <tbody>
            {% for hop in batch.recipe.hops.all %}
                {% if hop.use == "DRY HOP" %}
                <tr>
                    <td class="text-left">{{ hop.name }}</td>
                    <td class="text-left">{{ hop.use|title }}</td>
                    <td class="text-left">{{ hop.alpha_acids }}%</td>
                    <td class="text-left">{{ hop.amount|get_obj_attr:small_weight.0 }} {{small_weight.1}}</td>
                    <td class="text-left">{{ hop.time|floatformat }} {{hop.time_unit|lower}}(s)</td>
                </tr>
                {% endif %}
            {% endfor %}
        </tbody>
    </table>
    {% endif %}
</div>
"""

packaging_info_for_batch = """
<div class="mt-5 mb-5">
    <h5>Carbonation Guidline</h5>
    <table class="table table-sm">
        <tr>
        <th>British-style ales</th>
        <td>1.7 - 2.3</th>
        </tr>
        <tr>
        <th>Porter, stout</th>
        <td>1.9 - 2.4</th>
        </tr>
        <tr>
        <th>Belgian ales</th>
        <td>2.2 - 2.7</th>
        </tr>
        <tr>
        <th>European lagers</th>
        <td>2.2 - 2.7</th>
        </tr>
        <tr>
        <th>American ales and lagers</th>
        <td>2.4 - 2.8</th>
        </tr>
        <tr>
        <th>Lambic</th>
        <td>3.0 - 4.5</th>
        </tr>
        <tr>
        <th>Fruit lambic</th>
        <td>3.3 - 4.5 </th>
        </tr>
    </table>
</div>
"""

packaging_stats_for_batch = """
{% load brew_tags %}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>ABV:</td>
      <td class: "text-left" id="abv_batch_stats">{{ batch.get_abv|floatformat }} %</td>
   <tr>
   <tr>
      <td>Attenuation:</td>
      <td class: "text-left" id="attenuation_batch_stats">{{ batch.get_attenuation|floatformat }} %</td>
   <tr>
   <tr>
      <td>Calories:</td>
      <td class: "text-left" id="calories_batch_stats">{{ batch.get_calories|floatformat }} kcal/500ml</td>
   <tr>
</table>
"""


priming_info_for_batch = """
{% load brew_tags %}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>Priming sugar:</td>
      <td class: "text-left" id="priming_sugar_info"><span id="priming_sugar_info_span"></span> {{small_weight.1}}</td>
   <tr>
   <tr>
      <td>Amount of water:</td>
      <td class: "text-left" id="priming_water_info"><span id="priming_water_info_span"></span> {{volume.1}}</td>
   <tr>
</table>
"""

def _get_unit_choices(profile):
    # 
    if profile.general_units == "METRIC":
        volume_unit_choices = (("l", "l"),)
    elif profile.general_units == "IMPERIAL":
        volume_unit_choices = (("us_g", "us_g"),)
    else:
        raise ValueError(f"No unit choice {profile.general_units}")
    if profile.temperature_units == "CELSIUS":
        temp_unit_choices = (("c", "c"),)
    elif profile.temperature_units == "FAHRENHEIT":
        temp_unit_choices = (("f", "f"),)
    elif profile.temperature_units == "KELVIN":
        temp_unit_choices = (("k", "k"),)
    else:
        raise ValueError(f"No unit choice {profile.temperature_units}")
    gravity_unit_choices = (
        (
            profile.gravity_units.lower(),
            profile.gravity_units.lower()
        ),
    )
    return (volume_unit_choices, temp_unit_choices, gravity_unit_choices)


class BaseBatchForm(BSModalModelForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        volume_unit_choices, temp_unit_choices, gravity_unit_choices = _get_unit_choices(
            self.request.user.profile
        )

        if "recipe" in self.fields:
            grav_unit = self.request.user.profile.gravity_units.lower()
            if grav_unit == "plato":
                prec = 1
                un = "°P"
            else:
                prec = 4
                un = grav_unit.upper()
            self.fields["recipe"].queryset = models.Recipe.objects.filter(user=self.request.user)
            self.fields['recipe'].label_from_instance = lambda obj: "%s (%s, %s %s, %.0f IBU)" % (obj.name, obj.style, f"{round(getattr(obj.get_gravity(), grav_unit), prec)}", un, obj.get_ibu())
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
            self.fields.update({
                "grain_temperature": MeasurementField(
                    measurement=Temperature,
                    unit_choices=temp_unit_choices),
                "sparging_temperature": MeasurementField(
                    measurement=Temperature,
                    unit_choices=temp_unit_choices)})
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
                    Row(
                        Column(HTML(mash_info_for_batch), css_class='form-group mb-0'),
                        css_class='form-row'
                    )
                ),
                Div(
                    ButtonHolder(
                        Submit("save", "Save", css_class="btn-warning"),
                        Submit("next_stage", "Boil >")
                    )
                )
            )
        elif self.instance.stage == "BOIL":
            self.fields.update({
                "gravity_before_boil": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=gravity_unit_choices),
            })

            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Boil",
                        Field("gravity_before_boil"),
                        Row(
                            Column(HTML(boil_stats_for_batch), css_class='form-group col-md-5 mb-0'),
                            css_class='form-row'
                        ),
                    ),
                    Row(
                        Column(HTML(boil_info_for_batch), css_class='form-group mb-0'),
                        css_class='form-row'
                    )
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "< Mash", formnovalidate='formnovalidate'),
                        Submit("save", "Save", css_class="btn-warning"),
                        Submit("next_stage", "Primary >")
                    )
                )
            )
        elif self.instance.stage == "PRIMARY_FERMENTATION":
            self.fields.update({
                "primary_fermentation_temperature": MeasurementField(
                    measurement=Temperature,
                    required=False,
                    unit_choices=temp_unit_choices),
                "initial_gravity": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=gravity_unit_choices),
                "wort_volume": MeasurementField(
                    measurement=Volume,
                    unit_choices=volume_unit_choices),
                "boil_loss": MeasurementField(
                    measurement=Volume,
                    unit_choices=volume_unit_choices),
            })
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Primary Fermentation",
                        Field("initial_gravity"),
                        Field("wort_volume"),
                        Field("boil_loss"),
                        Field("primary_fermentation_temperature"),
                        Field("primary_fermentation_start_day"),
                        Row(
                            Column(HTML(primary_stats_for_batch), css_class='form-group col-md-5 mb-0'),
                            css_class='form-row'
                        ),
                    ),
                    Row(
                        Column(HTML(primary_info_for_batch), css_class='form-group mb-0'),
                        css_class='form-row'
                    )
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "< Boil", formnovalidate='formnovalidate'),
                        Submit("save", "Save", css_class="btn-warning"),
                        Submit("next_stage", "Secondary >")
                    )
                )
            )
        elif self.instance.stage == "SECONDARY_FERMENTATION":
            self.fields.update({
                "secondary_fermentation_temperature": MeasurementField(
                    measurement=Temperature,
                    required=False,
                    unit_choices=temp_unit_choices),
                "post_primary_gravity": MeasurementField(
                    measurement=BeerGravity,
                    required=False,
                    unit_choices=gravity_unit_choices),
            })
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset("Secondary Fermentation",
                        Field("post_primary_gravity"),
                        Field("secondary_fermentation_temperature"),
                        Field("secondary_fermentation_start_day"),
                        Field("dry_hops_start_day"),
                    ),
                    Row(
                        Column(HTML(secondary_info_for_batch), css_class='form-group mb-0'),
                        css_class='form-row'
                    )
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "< Primary", formnovalidate='formnovalidate'),
                        Submit("save", "Save", css_class="btn-warning"),
                        Submit("next_stage", "Packaging >")
                    )
                )
            )
        elif self.instance.stage == "PACKAGING":
            style = ""
            if getattr(self.instance, "carbonation_type", None) is not None:
                if getattr(self.instance, "carbonation_type", None).lower() == "forced":
                    style = "display:none"
            else:
                style = "display:none"
            self.fields.update({
                "end_gravity": MeasurementField(
                    measurement=BeerGravity,
                    unit_choices=gravity_unit_choices),
                "beer_volume": MeasurementField(
                    measurement=Volume,
                    unit_choices=volume_unit_choices),
                "priming_temperature": MeasurementField(
                    measurement=Temperature,
                    required=False,
                    unit_choices=temp_unit_choices),
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
                        Row(
                            Column(
                                Field("sugar_type"),
                                Field("priming_temperature"),
                                css_class="col-md-12"
                            ),
                            Column(HTML(priming_info_for_batch), css_class="col-md-3"),
                            css_class="refermentation-fields",
                            style=style
                        ),
                        Row(
                            Column(HTML(packaging_stats_for_batch), css_class='form-group col-md-3 mb-0'),
                            css_class='form-row'
                        ),
                    ),
                    Row(
                        Column(HTML(packaging_info_for_batch), css_class='form-group mb-0'),
                        css_class='form-row col-md-4 mb-0'
                    )
                ),
                Div(
                    ButtonHolder(
                        Submit("previous_stage", "< Secondary", formnovalidate='formnovalidate'),
                        Submit("save", "Save", css_class="btn-warning"),
                        Submit("finish", "Finish", css_class="btn-success")
                    )
                )
            )


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
        time_choices = (("MINUTE", "minute"), ("DAY", "day"))
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
                unit_choices=unit_choices, initial=Volume(l=20)),
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
                Fieldset("Recipe Information", Field("type"), Field("name"), Field("style"), Field('is_public')),
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
                        layouts.RecipeFormsetLayout('fermentables', "brewery/recipe/fermentable_formset.html"),
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
                        layouts.RecipeFormsetLayout('mash_steps', "brewery/recipe/mash_formset.html"),
                        css_class="form-row"
                    )
                ),
                Fieldset("Hops",
                    Row(
                        Column(HTML(HopInfoStatsHtml), css_class='form-group col-md-4 mb-0'),
                        css_class='form-row'
                    ),
                    Row(
                        layouts.RecipeFormsetLayout('hops', "brewery/recipe/hop_formset.html"),
                        css_class="form-row"
                    ),
                ),
                Fieldset("Yeasts", layouts.RecipeFormsetLayout('yeasts', "brewery/recipe/yeast_formset.html")),
                Fieldset("Extras", layouts.RecipeFormsetLayout('extras', "brewery/recipe/extra_formset.html")),
                Field('note'),
                HTML("<br>")
            ),
        )


    class Meta:
        model = models.Recipe
        exclude = ['user', ]


class RecipeImportForm(Form):
    json_file = FileField()


class BatchImportForm(Form):
    json_file = FileField()
