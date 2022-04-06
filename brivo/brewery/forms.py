from django.core.exceptions import ValidationError
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ugettext, pgettext, gettext
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
    Column,
)

from measurement.measures import Volume, Weight, Temperature
from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brewery.measurement_forms import MeasurementField
from brivo.brewery import layouts
from brivo.brewery import models


class PopRequestMixin:
    def get_form_kwargs(self):
        kwargs = super(PopRequestMixin, self).get_form_kwargs()
        kwargs.update({"request": self.request})
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
{{% load brew_tags %}}
{{% load i18n %}}
<div class="mashing mt-5 mb-5">
    <h5>{}</h5>
    <table class="table table-sm">
    <tbody>
        <tr>
        <th>{}</th>
        <td>{{{{batch.recipe.get_boil_volume|get_obj_attr:volume.0|floatformat}}}} {{{{volume.1}}}}</td>
        <tr>
        <tr>
        <th>{}</th>
        <td>{{{{batch.recipe.mash_efficiency|floatformat}}}}%</td>
        <tr>
        <tr>
        <th>{}</th>
        <td>{{{{batch.recipe.liquor_to_grist_ratio|floatformat}}}} {{{{volume.1}}}}/{{{{big_weight.1}}}}</td>
        <tr>
    </tbody>
    </table>
</div>
<div class="ingredients mt-5 mb-5">
    <h5>{}</h5>
    <table class="table table-sm">
        <thead>
            <tr>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
            </tr>
        </thead>
        <tbody>
            {{% for fermentable in batch.recipe.fermentables.all %}}
                <tr class="">
                    <td class="text-left">{{{{ fermentable.name }}}}</td>
                    <td class="text-left">{{{{ fermentable.get_type_display }}}}</td>
                    <td class="text-left">{{{{ fermentable.get_use_displayf|default:"---" }}}}</td>
                    <td class="text-left">{{{{ fermentable.color|get_obj_attr:color_units.0|floatformat }}}} {{{{color_units.1}}}}</td>
                    <td class="text-left">{{{{ fermentable.extraction }}}}%</td>
                    <td class="text-left">{{{{ fermentable.amount|get_obj_attr:big_weight.0|floatformat }}}} {{{{big_weight.1}}}}</td>
                </tr>
            {{% endfor %}}
        </tbody>
    </table>
</div>
"""

boil_info_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
<div class="ingredients mt-5 mb-5">
    <h5>{}</h5>
    <table class="table table-sm">
        <thead>
            <tr >
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
            </tr>
        </thead>
        <tbody>
            {{% for hop in batch.recipe.hops.all %}}
                {{% if hop.use != "DRY HOP" %}}
                <tr>
                    <td class="text-left">{{{{ hop.name }}}}</td>
                    <td class="text-left">{{{{ hop.use|title }}}}</td>
                    <td class="text-left">{{{{ hop.alpha_acids }}}}%</td>
                    <td class="text-left">{{{{ hop.amount|get_obj_attr:small_weight.0 }}}} {{{{small_weight.1}}}}</td>
                    <td class="text-left">{{{{ hop.time|floatformat }}}} {{{{hop.time_unit|lower}}}}</td>
                </tr>
                {{% endif %}}
            {{% endfor %}}
        </tbody>
    </table>
</div>
"""

boil_stats_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="expected_boil_volume_info">{{{{ batch.recipe.get_boil_volume|get_obj_attr:volume.0|floatformat }}}}  {{{{volume.1}}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="expected_preboil_gravity_info">{{{{ batch.recipe.get_preboil_gravity|get_obj_attr:gravity_units.0|floatformat}}}} {{{{gravity_units.1}}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="primary_volume_info">{{{{ batch.recipe.boil_time }}}} Min</td>
   <tr>
</table>
"""

primary_info_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
<div class="ingredients mt-5 mb-5">
    <h5>{}</h5>
    <table class="table table-sm">
        <thead>
            <tr >
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
            </tr>
        </thead>
        <tbody>
            {{% for yeast in batch.recipe.yeasts.all %}}
                <tr>
                    <td class="text-left">{{{{ yeast.name }}}}</td>
                    <td class="text-left">{{{{ yeast.lab }}}}</td>
                    <td class="text-left">{{{{ yeast.type|title }}}}</td>
                    <td class="text-left">{{{{ yeast.attenuation|floatformat }}}}%</td>
                    <td class="text-left">{{{{ yeast.form|title }}}}</td>
                    <td class="text-left">{{{{ yeast.amount|get_obj_attr:small_weight.0|floatformat }}}} {{{{small_weight.1}}}}</td>
                </tr>
            {{% endfor %}}
    </table>
</div>
<div class="checks mt-5 mb-5">
    <h5>{}</h5>
    <button type="button" class="mr-1 bs-modal read-recipe btn btn-sm btn-primary" data-form-url="{{% url 'brewery:batch-fermentation_check-create' batch.pk %}}">
        <span class="fa fa-plus"></span> {}
    </button>
    {{% if batch.fermentation_checks.all.count > 0 %}}
    <table class="table table-sm mt-2">
        <thead>
            <tr >
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
            </tr>
        </thead>
        <tbody>
            {{% for check in batch.fermentation_checks.all|dictsort:"sample_day" %}}
                <tr>
                    <td class="text-left">{{{{ check.sample_day }}}} ({{{{check.sample_day|timesince}}}})</td>
                    <td class="text-left">{{{{ check.gravity|get_obj_attr:gravity_units.0|floatformat}}}} {{{{gravity_units.1}}}}</td>
                    <td class="text-left">{{% if check.beer_temperature %}}{{{{ check.beer_temperature|get_obj_attr:temp_units.0|floatformat}}}}{{% else %}}---{{% endif %}} {{% if check.beer_temperature %}} {{{{ temp_units.1 }}}} {{% endif %}}</td>
                    <td class="text-left">{{% if check.ambient_temperature %}}{{{{ check.ambient_temperature|get_obj_attr:temp_units.0|floatformat}}}}{{% else %}}---{{% endif %}} {{% if check.ambient_temperature %}} {{{{ temp_units.1 }}}} {{% endif %}}</td>
                    <td class="text-left">{{% if check.comment %}}{{{{ check.comment }}}}{{% else %}}---{{% endif %}}</td>
                    <td class="text-center">
                        {{% if user.is_authenticated %}}
                        <button type="button" class="bs-modal update-ferm-check btn btn-sm btn-primary" data-form-url="{{% url 'brewery:batch-fermentation_check-update' batch.pk check.pk %}}">
                        <span class="fa fa-edit"></span>
                        </button>
                        <button type="button" class="bs-modal delete-ferm-check btn btn-sm btn-danger" data-form-url="{{% url 'brewery:batch-fermentation_check-delete' batch.pk check.pk %}}">
                        <span class="fa fa-trash"></span>
                        </button>
                        {{% endif %}}
                    </td>
                </tr>
            {{% endfor %}}
        </tbody>
    </table>
    {{% endif %}}
</div>
"""

primary_stats_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="expected_gravity_info">{{{{ batch.recipe.get_gravity|get_obj_attr:gravity_units.0|floatformat}}}} {{{{gravity_units.1}}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="expected_boil_volume_with_trub_loss_info">{{{{ batch.recipe.get_primary_volume|get_obj_attr:volume.0|floatformat }}}}  {{{{volume.1}}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="expected_boil_loss_info">{{{{ batch.recipe.get_boil_loss_volume|get_obj_attr:volume.0|floatformat }}}}  {{{{volume.1}}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="primary_volume_info">{{{{ batch.get_ibu|floatformat|default:"---" }}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="actual_mash_efficiency_info">{{{{ batch.get_actuall_mash_efficiency|floatformat|default:"---" }}}}%</td>
   <tr>
</table>
"""


secondary_info_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
<div class="ingredients mt-5 mb-5">
    {{% if batch.recipe.hops.all|count_dry_hops > 0 %}}
    <h5>{}</h5>
    <table class="table table-sm">
        <thead>
            <tr >
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
                <th class="text-left" scope="col">{}</th>
            </tr>
        </thead>
        <tbody>
            {{% for hop in batch.recipe.hops.all %}}
                {{% if hop.use == "DRY HOP" %}}
                <tr>
                    <td class="text-left">{{{{ hop.name }}}}</td>
                    <td class="text-left">{{{{ hop.use|title }}}}</td>
                    <td class="text-left">{{{{ hop.alpha_acids }}}}%</td>
                    <td class="text-left">{{{{ hop.amount|get_obj_attr:small_weight.0 }}}} {{{{small_weight.1}}}}</td>
                    <td class="text-left">{{{{ hop.time|floatformat }}}} {{{{hop.time_unit|lower}}}}</td>
                </tr>
                {{% endif %}}
            {{% endfor %}}
        </tbody>
    </table>
    {{% endif %}}
</div>
"""

packaging_info_for_batch = """
{{% load i18n %}}
<div class="mt-5 mb-5">
    <h5>{}</h5>
    <table class="table table-sm">
        <tr>
        <th>{}</th>
        <td>1.7 - 2.3</th>
        </tr>
        <tr>
        <th>{}</th>
        <td>1.9 - 2.4</th>
        </tr>
        <tr>
        <th>{}</th>
        <td>2.2 - 2.7</th>
        </tr>
        <tr>
        <th>{}</th>
        <td>2.2 - 2.7</th>
        </tr>
        <tr>
        <th>{}</th>
        <td>2.4 - 2.8</th>
        </tr>
        <tr>
        <th>{}</th>
        <td>3.0 - 4.5</th>
        </tr>
        <tr>
        <th>{}</th>
        <td>3.3 - 4.5 </th>
        </tr>
    </table>
</div>
"""

packaging_stats_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="abv_batch_stats">{{{{ batch.get_abv|floatformat }}}} %</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="attenuation_batch_stats">{{{{ batch.get_attenuation|floatformat }}}} %</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="calories_batch_stats">{{{{ batch.get_calories|floatformat }}}} kcal/500ml</td>
   <tr>
</table>
"""

priming_info_for_batch = """
{{% load brew_tags %}}
{{% load i18n %}}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="priming_sugar_info"><span id="priming_sugar_info_span"></span> {{{{small_weight.1}}}}</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="priming_water_info"><span id="priming_water_info_span"></span> {{{{volume.1}}}}</td>
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
        (profile.gravity_units.lower(), profile.gravity_units.lower()),
    )
    return (volume_unit_choices, temp_unit_choices, gravity_unit_choices)


class BaseBatchForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        (
            volume_unit_choices,
            temp_unit_choices,
            gravity_unit_choices,
        ) = _get_unit_choices(self.request.user.profile)

        if "recipe" in self.fields:
            grav_unit = self.request.user.profile.gravity_units.lower()
            if grav_unit == "plato":
                prec = 1
                un = "°P"
            else:
                prec = 4
                un = grav_unit.upper()
            self.fields["recipe"].queryset = models.Recipe.objects.filter(
                user=self.request.user
            )
            self.fields[
                "recipe"
            ].label_from_instance = lambda obj: "%s (%s, %s %s, %.0f IBU)" % (
                obj.name,
                obj.style,
                f"{round(getattr(obj.get_gravity(), grav_unit), prec)}",
                un,
                obj.get_ibu(),
            )
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "POST"
        # self.helper.form_class = 'form-horizontal'
        self.helper.label_class = "col-md-6 create-label"
        self.helper.field_class = "col-md-6"
        if self.instance.stage == "INIT":
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset(
                        _("Base Recipe Selection"),
                        Field("recipe"),
                    ),
                ),
                Div(ButtonHolder(Submit("next_stage", _("Brew It!")))),
            )
        elif self.instance.stage == "MASHING":
            self.fields.update(
                {
                    "grain_temperature": MeasurementField(
                        label=_("Grain Temperature"),
                        measurement=Temperature,
                        unit_choices=temp_unit_choices,
                    ),
                    "sparging_temperature": MeasurementField(
                        label=_("Sparging Temperature"),
                        measurement=Temperature,
                        unit_choices=temp_unit_choices,
                    ),
                }
            )
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset(
                        _("Mash"),
                        Field("name"),
                        Field("batch_number"),
                        Field("brewing_day"),
                        Field("grain_temperature"),
                        Field("sparging_temperature"),
                    ),
                    Row(
                        Column(
                            HTML(
                                mash_info_for_batch.format(
                                    _("Mash Information"),
                                    _("Boil Size"),
                                    _("Mash Efficiency"),
                                    _("Liquor-to-Grist Ratio"),
                                    _("Fermentables"),
                                    _("Name"),
                                    _("Type"),
                                    _("Use"),
                                    _("Color"),
                                    _("Extraction"),
                                    _("Amount"),
                                )
                            ),
                            css_class="form-group mb-0",
                        ),
                        css_class="form-row",
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit("save", ugettext("Save"), css_class="btn-warning"),
                        Submit("next_stage", ugettext("Boil") + " >"),
                    )
                ),
            )
        elif self.instance.stage == "BOIL":
            self.fields.update(
                {
                    "gravity_before_boil": MeasurementField(
                        label=_("Gravity Before Boil"),
                        measurement=BeerGravity,
                        unit_choices=gravity_unit_choices,
                    ),
                }
            )

            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset(
                        _("Boil"),
                        Field("gravity_before_boil"),
                        Row(
                            Column(
                                HTML(
                                    boil_stats_for_batch.format(
                                        _("Expected Boil Volume"),
                                        _("Expected Pre-Boil Gravity"),
                                        _("Boil Time"),
                                    )
                                ),
                                css_class="form-group col-md-5 mb-0",
                            ),
                            css_class="form-row",
                        ),
                    ),
                    Row(
                        Column(
                            HTML(
                                boil_info_for_batch.format(
                                    _("Hops"),
                                    _("Name"),
                                    _("Use"),
                                    _("Alpha Acids"),
                                    _("Amount"),
                                    _("Time"),
                                )
                            ),
                            css_class="form-group mb-0",
                        ),
                        css_class="form-row",
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit(
                            "previous_stage",
                            "< " + ugettext("Mash"),
                            formnovalidate="formnovalidate",
                        ),
                        Submit("save", ugettext("Save"), css_class="btn-warning"),
                        Submit(
                            "next_stage",
                            pgettext("fermentation stage", "Primary") + " >",
                        ),
                    )
                ),
            )
        elif self.instance.stage == "PRIMARY_FERMENTATION":
            self.fields.update(
                {
                    "primary_fermentation_temperature": MeasurementField(
                        label=_("Primary Fermentation Temperature"),
                        measurement=Temperature,
                        required=False,
                        unit_choices=temp_unit_choices,
                    ),
                    "initial_gravity": MeasurementField(
                        label=_("Initial Gravity"),
                        measurement=BeerGravity,
                        unit_choices=gravity_unit_choices,
                    ),
                    "wort_volume": MeasurementField(
                        label=_("Wort Volume"),
                        measurement=Volume,
                        unit_choices=volume_unit_choices,
                    ),
                    "boil_loss": MeasurementField(
                        label=_("Boil Loss"),
                        measurement=Volume,
                        unit_choices=volume_unit_choices,
                    ),
                }
            )
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset(
                        _("Primary Fermentation"),
                        Field("initial_gravity"),
                        Field("wort_volume"),
                        Field("boil_loss"),
                        Field("primary_fermentation_temperature"),
                        Field("primary_fermentation_start_day"),
                        Row(
                            Column(
                                HTML(
                                    primary_stats_for_batch.format(
                                        _("Expected Gravity"),
                                        _("Expected Volume With Trub Loss"),
                                        _("Expected Boil Loss"),
                                        _("Batch IBU"),
                                        _("Actual Mash Efficiency"),
                                    )
                                ),
                                css_class="form-group col-md-5 mb-0",
                            ),
                            css_class="form-row",
                        ),
                    ),
                    Row(
                        Column(
                            HTML(
                                primary_info_for_batch.format(
                                    _("Yeasts"),
                                    _("Name"),
                                    _("Lab"),
                                    _("Type"),
                                    _("Attenuation"),
                                    _("Form"),
                                    _("Amount"),
                                    _("Fermentation Checks"),
                                    _("Add Fermentation Check"),
                                    _("Sample Day"),
                                    _("Gravity"),
                                    _("Beer Temperature"),
                                    _("Ambient Temperature"),
                                    _("Comment"),
                                )
                            ),
                            css_class="form-group mb-0",
                        ),
                        css_class="form-row",
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit(
                            "previous_stage",
                            "< " + ugettext("Boil"),
                            formnovalidate="formnovalidate",
                        ),
                        Submit("save", ugettext("Save"), css_class="btn-warning"),
                        Submit("next_stage", ugettext("Secondary") + " >"),
                    )
                ),
            )
        elif self.instance.stage == "SECONDARY_FERMENTATION":
            self.fields.update(
                {
                    "secondary_fermentation_temperature": MeasurementField(
                        label=_("Secondary Fermentation Temperature"),
                        measurement=Temperature,
                        required=False,
                        unit_choices=temp_unit_choices,
                    ),
                    "post_primary_gravity": MeasurementField(
                        label=_("Post-primary Gravity"),
                        measurement=BeerGravity,
                        required=False,
                        unit_choices=gravity_unit_choices,
                    ),
                }
            )
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset(
                        _("Secondary Fermentation"),
                        Field("post_primary_gravity"),
                        Field("secondary_fermentation_temperature"),
                        Field("secondary_fermentation_start_day"),
                        Field("dry_hops_start_day"),
                    ),
                    Row(
                        Column(
                            HTML(
                                secondary_info_for_batch.format(
                                    _("Hops"),
                                    _("Name"),
                                    _("Use"),
                                    _("Alpha Acids"),
                                    _("Amount"),
                                    _("Time"),
                                )
                            ),
                            css_class="form-group mb-0",
                        ),
                        css_class="form-row",
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit(
                            "previous_stage",
                            "< " + pgettext("fermentation stage", "Primary"),
                            formnovalidate="formnovalidate",
                        ),
                        Submit("save", ugettext("Save"), css_class="btn-warning"),
                        Submit("next_stage", ugettext("Packaging") + " >"),
                    )
                ),
            )
        elif self.instance.stage == "PACKAGING":
            style = ""
            if getattr(self.instance, "carbonation_type", None) is not None:
                if getattr(self.instance, "carbonation_type", None).lower() == "forced":
                    style = "display:none"
            else:
                style = "display:none"
            self.fields.update(
                {
                    "end_gravity": MeasurementField(
                        label=_("End Gravity"),
                        measurement=BeerGravity,
                        unit_choices=gravity_unit_choices,
                    ),
                    "beer_volume": MeasurementField(
                        label=_("Beer Volume"),
                        measurement=Volume,
                        unit_choices=volume_unit_choices,
                    ),
                    "priming_temperature": MeasurementField(
                        label=_("Priming Temperature"),
                        measurement=Temperature,
                        required=False,
                        unit_choices=temp_unit_choices,
                    ),
                }
            )
            self.helper.layout = Layout(
                Div(
                    Hidden("stage", self.instance.stage),
                    Fieldset(
                        _("Packaging"),
                        Field("packaging_date"),
                        Field("end_gravity"),
                        Field("beer_volume"),
                        Field("carbonation_type"),
                        Field("carbonation_level"),
                        Row(
                            Column(
                                Field("sugar_type"),
                                Field("priming_temperature"),
                                css_class="col-md-12",
                            ),
                            Column(
                                HTML(
                                    priming_info_for_batch.format(
                                        _("Priming Sugar"),
                                        _("Amount of Water"),
                                    )
                                ),
                                css_class="col-md-3",
                            ),
                            css_class="refermentation-fields",
                            style=style,
                        ),
                        Row(
                            Column(
                                HTML(
                                    packaging_stats_for_batch.format(
                                        _("ABV"),
                                        _("Attenuation"),
                                        _("Calories"),
                                    )
                                ),
                                css_class="form-group col-md-3 mb-0",
                            ),
                            css_class="form-row",
                        ),
                    ),
                    Row(
                        Column(
                            HTML(
                                packaging_info_for_batch.format(
                                    _("Carbonation Guidline"),
                                    _("British-Style Ales"),
                                    _("Porter, Stout"),
                                    _("Belgian Ales"),
                                    _("European Lagers"),
                                    _("American Ales and Lagers"),
                                    _("Lambic"),
                                    _("Fruit Lambic"),
                                )
                            ),
                            css_class="form-group mb-0",
                        ),
                        css_class="form-row col-md-4 mb-0",
                    ),
                ),
                Div(
                    ButtonHolder(
                        Submit(
                            "previous_stage",
                            "< " + ugettext("Secondary"),
                            formnovalidate="formnovalidate",
                        ),
                        Submit("save", ugettext("Save"), css_class="btn-warning"),
                        Submit("finish", ugettext("Finish"), css_class="btn-success"),
                    )
                ),
            )


class FermentationCheckModelForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super(FermentationCheckModelForm, self).__init__(*args, **kwargs)
        (
            volume_unit_choices,
            temp_unit_choices,
            gravity_unit_choices,
        ) = _get_unit_choices(self.request.user.profile)
        self.fields.update(
            {
                "beer_temperature": MeasurementField(
                    label=_("Beer Temperature"),
                    measurement=Temperature,
                    unit_choices=temp_unit_choices,
                    required=False,
                ),
                "ambient_temperature": MeasurementField(
                    label=_("Ambient Temperature"),
                    measurement=Temperature,
                    unit_choices=temp_unit_choices,
                    required=False,
                ),
                "gravity": MeasurementField(
                    label=_("Gravity"),
                    measurement=BeerGravity,
                    unit_choices=gravity_unit_choices,
                ),
            }
        )

    class Meta:
        model = models.FermentationCheck
        fields = [
            "gravity",
            "beer_temperature",
            "ambient_temperature",
            "sample_day",
            "comment",
        ]


class FermentableModelForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super(FermentableModelForm, self).__init__(*args, **kwargs)
        self.fields.update(
            {
                "color": MeasurementField(
                    label=_("Color"),
                    measurement=BeerColor,
                    unit_choices=(
                        (
                            self.request.user.profile.color_units.lower(),
                            self.request.user.profile.color_units.lower(),
                        ),
                    ),
                )
            }
        )

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
            raise ValueError(
                f"No unit choice {self.request.user.profile.general_units}"
            )
        self.fields.update(
            {
                "temp_min": MeasurementField(
                    label=_("Min Temperature"),
                    measurement=Temperature,
                    unit_choices=unit_choices,
                ),
                "temp_max": MeasurementField(
                    label=_("Max Temperature"),
                    measurement=Temperature,
                    unit_choices=unit_choices,
                ),
            }
        )

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
        self.fields.update(
            {
                "color_min": MeasurementField(
                    label=_("Color Min"),
                    measurement=BeerColor,
                    unit_choices=((user_color_unit, user_color_unit),),
                ),
                "color_max": MeasurementField(
                    label=_("Color Max"),
                    measurement=BeerColor,
                    unit_choices=((user_color_unit, user_color_unit),),
                ),
                "og_min": MeasurementField(
                    label=_("OG Min"),
                    measurement=BeerGravity,
                    unit_choices=((user_gravity_unit, user_gravity_unit),),
                ),
                "og_max": MeasurementField(
                    label=_("OG Max"),
                    measurement=BeerGravity,
                    unit_choices=((user_gravity_unit, user_gravity_unit),),
                ),
                "fg_min": MeasurementField(
                    label=_("FG Min"),
                    measurement=BeerGravity,
                    unit_choices=((user_gravity_unit, user_gravity_unit),),
                ),
                "fg_max": MeasurementField(
                    label=_("FG Max"),
                    measurement=BeerGravity,
                    unit_choices=((user_gravity_unit, user_gravity_unit),),
                ),
            }
        )

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
        self.fields.update(
            {
                "amount": MeasurementField(
                    label=_("Amount"), measurement=Weight, unit_choices=unit_choices
                ),
                "color": MeasurementField(
                    label=_("Color"), measurement=BeerColor, unit_choices=color_choices
                ),
            }
        )

    class Meta:
        model = models.IngredientFermentable
        exclude = ()


IngredientFermentableFormSet = inlineformset_factory(
    models.Recipe,
    models.IngredientFermentable,
    form=IngredientFermentableForm,
    fields=["name", "type", "use", "color", "extraction", "amount"],
    extra=1,
    can_delete=True,
    formset=BaseFormSet,
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
        self.fields.update(
            {
                "amount": MeasurementField(
                    label=_("Amount"), measurement=Weight, unit_choices=unit_choices
                ),
                "time_unit": ChoiceField(label=_("Time Unit"), choices=time_choices),
            }
        )

    class Meta:
        model = models.IngredientHop
        exclude = ()


IngredientHopFormSet = inlineformset_factory(
    models.Recipe,
    models.IngredientHop,
    form=IngredientHopForm,
    fields=["name", "use", "alpha_acids", "amount", "time", "time_unit"],
    extra=1,
    can_delete=True,
    formset=BaseFormSet,
)


class IngredientYeastForm(PopRequestMixin, ModelForm):
    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        self.fields.update(
            {
                "amount": MeasurementField(
                    label=_("Amount"), measurement=Weight, unit_choices=unit_choices
                ),
            }
        )

    class Meta:
        model = models.IngredientYeast
        exclude = ()


IngredientYeastFormSet = inlineformset_factory(
    models.Recipe,
    models.IngredientYeast,
    form=IngredientYeastForm,
    fields=["name", "type", "form", "attenuation", "amount", "lab"],
    extra=1,
    can_delete=True,
    formset=BaseFormSet,
)


class IngredientExtraForm(PopRequestMixin, ModelForm):
    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("g", "g"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("oz", "oz"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        self.fields.update(
            {
                "amount": MeasurementField(
                    label=_("Amount"), measurement=Weight, unit_choices=unit_choices
                )
            }
        )

    class Meta:
        model = models.IngredientExtra
        exclude = ()


IngredientExtraFormSet = inlineformset_factory(
    models.Recipe,
    models.IngredientExtra,
    form=IngredientExtraForm,
    fields=["name", "type", "use", "amount", "time", "time_unit"],
    extra=1,
    can_delete=True,
    formset=BaseFormSet,
)


class MashStepForm(PopRequestMixin, ModelForm):
    def add_user_restrictions_to_field(self, request):
        if request.user.profile.general_units == "METRIC":
            unit_choices = (("c", "c"),)
        elif request.user.profile.general_units == "IMPERIAL":
            unit_choices = (("f", "f"),)
        else:
            raise ValueError(f"No unit choice {request.user.profile.general_units}")
        self.fields.update(
            {
                "temperature": MeasurementField(
                    label=_("Temperature"),
                    measurement=Temperature,
                    unit_choices=unit_choices,
                ),
            }
        )

    class Meta:
        model = models.MashStep
        exclude = ()


MashStepFormSet = inlineformset_factory(
    models.Recipe,
    models.MashStep,
    form=MashStepForm,
    fields=["temperature", "time"],
    extra=1,
    can_delete=True,
    formset=BaseFormSet,
)

batch_info_stats = """
{{% load i18n %}}
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="boil_volume_info">---</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="preboil_gravity_info">---</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="primary_volume_info">---</td>
   <tr>
   <tr>
      <td>{}:</td>
      <td class: "text-left" id="secondary_volume_info">---</td>
   <tr>
</table>
"""

fermentable_info_stats = """
{{% load i18n %}}
<div>
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}</td>
      <td class: "text-left" id="gravity_info">---</td>
      <td class: "text-left" id="gravity_styleinfo">---</td>
   <tr>
   <tr>
      <td>Expected ABV</td>
      <td class: "text-left" id="abv_info">---</td>
      <td class: "text-left" id="abv_styleinfo">---</td>
   <tr>
   <tr>
      <td>{}</td>
      <td class: "text-left" id="color_info">---</td>
      <td class: "text-left" id="color_styleinfo">---</td>
   <tr>
</table>
</div>
"""
hop_info_stats = """
{{% load i18n %}}
<div>
</br>
<table class="table" style="background:#dedede">
   <tr>
      <td>{}</td>
      <td class: "text-left" id="ibu_info">---</td>
      <td class: "text-left" id="ibu_styleinfo">---</td>
   <tr>
   <tr>
      <td>{}</td>
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
            raise ValueError(
                f"No unit choice {self.request.user.profile.general_units}"
            )
        self.fields.update(
            {
                "expected_beer_volume": MeasurementField(
                    label=_("Expected Beer Volume"),
                    measurement=Volume,
                    unit_choices=unit_choices,
                    initial=Volume(l=20),
                ),
            }
        )

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.add_input(Submit("submit", _("Submit"), css_class="btn-primary"))
        self.helper.form_method = "POST"
        # self.helper.form_class = 'form-horizontal'
        self.helper.label_class = "col-md-6 create-label"
        self.helper.field_class = "col-md-6"
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    _("Recipe Information"),
                    Field("type"),
                    Field("name"),
                    Field("style"),
                    Field("is_public"),
                ),
                Fieldset(
                    _("Batch Information"),
                    Row(
                        Column(
                            Field("expected_beer_volume"),
                            css_class="form-group col-md-6 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            AppendedText("boil_time", "min"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            AppendedText("evaporation_rate", "%/h"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            AppendedText("boil_loss", "%"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            AppendedText("trub_loss", "%"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            AppendedText("dry_hopping_loss", "%"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        Column(
                            HTML(
                                batch_info_stats.format(
                                    _("Boil Volume"),
                                    _("Pre-boil Gravity"),
                                    _("Primary Volume"),
                                    _("Secondary Volume"),
                                )
                            ),
                            css_class="form-group col-md-3 mb-0",
                        ),
                        css_class="form-row",
                    ),
                ),
                Fieldset(
                    _("Fermentables"),
                    Row(
                        Column(
                            HTML(
                                fermentable_info_stats.format(
                                    _("Gravity"),
                                    _("Color"),
                                )
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        layouts.RecipeFormsetLayout(
                            "fermentables", "brewery/recipe/fermentable_formset.html"
                        ),
                        css_class="form-row",
                    ),
                ),
                Fieldset(
                    _("Mash"),
                    Row(
                        Column(
                            AppendedText("mash_efficiency", "%"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        Column(
                            AppendedText("liquor_to_grist_ratio", "?"),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        layouts.RecipeFormsetLayout(
                            "mash_steps", "brewery/recipe/mash_formset.html"
                        ),
                        css_class="form-row",
                    ),
                ),
                Fieldset(
                    _("Hops"),
                    Row(
                        Column(
                            HTML(
                                hop_info_stats.format(
                                    _("Bitterness"),
                                    _("Bitterness Ratio"),
                                )
                            ),
                            css_class="form-group col-md-4 mb-0",
                        ),
                        css_class="form-row",
                    ),
                    Row(
                        layouts.RecipeFormsetLayout(
                            "hops", "brewery/recipe/hop_formset.html"
                        ),
                        css_class="form-row",
                    ),
                ),
                Fieldset(
                    _("Yeasts"),
                    layouts.RecipeFormsetLayout(
                        "yeasts", "brewery/recipe/yeast_formset.html"
                    ),
                ),
                Fieldset(
                    _("Extras"),
                    layouts.RecipeFormsetLayout(
                        "extras", "brewery/recipe/extra_formset.html"
                    ),
                ),
                Field("note"),
                HTML("<br>"),
            ),
        )

    class Meta:
        model = models.Recipe
        exclude = [
            "user",
        ]


class RecipeImportForm(Form):
    file = FileField()
    filetype = ChoiceField(choices=(("beerxml", "BeerXML"), ("json", "JSON")))


class BatchImportForm(Form):
    json_file = FileField()
