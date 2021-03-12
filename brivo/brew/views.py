import re
import json
import datetime, pytz
from django.conf import settings
from django.templatetags.static import static
from django.db import transaction
from django.http import request, JsonResponse, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.forms import modelform_factory
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from bootstrap_modal_forms.generic import (
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)
from attrdict import AttrDict
from django_weasyprint import WeasyTemplateResponseMixin
# from . import constants
from measurement.measures import Volume, Weight, Temperature
from brivo.utils.measures import BeerColor, BeerGravity
from brivo.brew import forms
from brivo.utils import functions
from brivo.brew.forms import (
    BaseBatchForm,
    FermentableModelForm,
    HopModelForm,
    YeastModelForm,
    ExtraModelForm,
    StyleModelForm,
    RecipeModelForm,
    FermentableIngredientFormSet)
from brivo.brew.models import (
    Batch,
    BATCH_STAGE_ORDER,
    Fermentable,
    Hop,
    Yeast,
    Extra,
    Style,
    Recipe,
    RecipeCalculatorMixin)
from brivo.users.models import User
from brivo.brew import filters


_FLOAT_REGEX = re.compile(r"^-?(?:\d+())?(?:\.\d*())?(?:e-?\d+())?(?:\2|\1\3)$")
_INT_REGEX = re.compile(r"^(?<![\d.])[0-9]+(?![\d.])$")
_EMAIL_REGEX = re.compile(r"(.+@[a-zA-Z0-9\.]+,?){1,}")


def _get_units_for_user(user):
    data = {}
    if user.profile.general_units.lower() == "metric":
        data["small_weight"] = ("g", "g")
        data["big_weight"] = ("kg", "kg")
        data["volume"] = ("l", "l")
    else:
        data["small_weight"] = ("oz", "g")
        data["big_weight"] = ("lb", "lb")
        data["volume"] = ("us_g", "US Gal")
    if user.profile.gravity_units.lower() == "plato":
        data["gravity_units"] = ("Plato", "°P")
    else:
        data["gravity_units"] = ("SG", "SG")
    if user.profile.color_units.lower() == "ebc":
        data["color_units"] = ("EBC", "EBC")
    else:
        data["color_units"] = ("SRM", "SRM")
    if user.profile.temperature_units.lower() == "celsius":
        data["temp_units"] = ("c", "°C")
    elif user.profile.temperature_units.lower() == "fahrenheit":
        data["temp_units"] = ("f", "°F")
    else:
        data["temp_units"] = ("k", "K")
    return data


def _convert_type(data):
    """Check and convert the type of variable"""
    if isinstance(data, dict):
        return _clean_data(data)
    if _FLOAT_REGEX.match(data) is not None:  # Floats
        return float(data)
    elif _INT_REGEX.match(data) is not None:  # Integers
        return int(data)
    elif data == "True" or data == "true":
        return True
    elif data == "False" or data == "false":
        return False
    else:
        return str(data)  # The rest is string


def _clean_data(data):
    new_data = {}
    for k, v in data.items():
        new_data[k] = _convert_type(v)
    return new_data

measures_map = {
    "temperature": Temperature,
    "amount": Weight,
    "volume": Volume,
    "color": BeerColor
}

def _convert_to_measure(d):
    for k, v in d.items():
        if k.endswith("_unit") and k not in ["time_unit"]:
            new_k = "_".join(k.split("_")[:-1])
            if d[new_k]:
                d[new_k] = measures_map[new_k](**{v: d[new_k]})
    return d

def _is_valid(v):
    return v.get("amount", "") != ""


class DummyRecipe(RecipeCalculatorMixin, AttrDict):
    def get_fermentables(self):
        return self.fermentables

    def get_yeasts(self):
        return self.yeasts

    def get_hops(self):
        return self.hops


def get_recipe_data(request):
    form = request.POST.get('form', None)
    input_data = _clean_data(json.loads(form))
    for f in ["fermentables", "hops", "extras", "mash_steps", "yeasts"]:
        input_data[f] = [_convert_to_measure(v) for v in input_data[f].values() if _is_valid(v)]
    if input_data["general_units"] == "METRIC":
        volume_unit = "l"
    else:
        volume_unit = "us_g"
    
    input_data["expected_beer_volume"] = Volume(**{volume_unit: input_data["expected_beer_volume"]})
    input_data = DummyRecipe(input_data)
    try:
        boil_volume = f"{round(getattr(input_data.get_boil_volume(), volume_unit.lower()), 2)} {volume_unit.lower()}"
    except Exception as exc:
        print(exc)
        boil_volume = "---"
    try:
        primary_volume = f"{round(getattr(input_data.get_primary_volume(), volume_unit.lower()), 2)} {volume_unit.lower()}"
    except Exception as exc:
        print(exc)
        primary_volume = "---"
    try:
        secondary_volume = f"{round(getattr(input_data.get_secondary_volume(), volume_unit.lower()), 2)} {volume_unit.lower()}"
    except Exception as exc:
        print(exc)
        secondary_volume = "---"
    try:
        color_hex = functions.get_hex_color_from_srm(input_data.get_color().srm)
        color = f"{round(getattr(input_data.get_color(), input_data.color_units.lower()), 1)} {input_data.color_units}"
    except Exception as exc:
        print(exc)
        color_hex = "#FFFFFF"
        color = "---"
    try:
        if input_data.gravity_units.lower() == "plato":
            prec = 1
            un = "°P"
        else:
            prec = 4
            un = input_data.gravity_units.upper()
        preboil_gravity = f"{round(getattr(input_data.get_preboil_gravity(), input_data.gravity_units.lower()), prec)} {un}"
    except Exception as exc:
        print(exc)
        preboil_gravity = "---"
    try:
        if input_data.gravity_units.lower() == "plato":
            prec = 1
            un = "°P"
        else:
            prec = 4
            un = input_data.gravity_units.upper()
        gravity = f"{round(getattr(input_data.get_gravity(), input_data.gravity_units.lower()), prec)} {un}"
    except Exception as exc:
        print(exc)
        gravity = "---"
    try:
        abv = f"{round(input_data.get_abv(), 1)} %"
    except Exception as exc:
        print(exc)
        abv = "---"
    try:
        ibu = f"{round(input_data.get_ibu(), 1)} IBU"
    except Exception as exc:
        print(exc)
        ibu = "---"
    try:
        bitterness_ratio = f"{round(input_data.get_bitterness_ratio(), 1)}"
    except Exception as exc:
        print(exc)
        bitterness_ratio = "---"
    data = {
        "boil_volume": boil_volume,
        "primary_volume": primary_volume,
        "secondary_volume": secondary_volume,
        "color": color,
        "color_hex": color_hex,
        "preboil_gravity": preboil_gravity,
        "gravity": gravity,
        "abv": abv,
        "ibu": ibu,
        "bitterness_ratio": bitterness_ratio,
    }
    return JsonResponse(data)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class BaseAutocomplete(LoginRequiredMixin, ListView):
    http_method_allowed = ('GET', 'POST')

    def dispatch(self, request, *args, **kwargs):
        if request.method.upper() not in self.http_method_allowed:
            return HttpResponseNotAllowed(self.http_method_allowed)

        self.q = request.GET.get('q', '')
        return super(ListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs

    def render_to_response(self, context):
        """Return a JSON response in correct format."""

        return JsonResponse(
            {
                'suggestions': self.get_results(context),
            })

    def get_results(self, context):
        raise NotImplementedError

class FermentableAutocomplete(BaseAutocomplete):
    model = Fermentable

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        return [
            {
                'data': {
                    "name": result.name,
                    "type": result.type,
                    "color": getattr(result.color, self.request.user.profile.color_units.lower()),
                    "extraction": result.extraction
                },
                'value': result.name,
            } for result in context['object_list']
        ]


class HopAutocomplete(BaseAutocomplete):
    model = Hop

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        return [
            {
                'data': {
                    "name": result.name,
                    "alpha_acids": result.alpha_acids
                },
                'value': result.name,
            } for result in context['object_list']
        ]


class YeastAutocomplete(BaseAutocomplete):
    model = Yeast

    def get_results(self, context):
        """Return data for the 'results' key of the response."""

        return [
            {
                'data': {
                    "name": result.name,
                    "lab": result.lab,
                    "attenuation": result.get_average_attenuation(),
                    "form": result.form,
                    "type": result.type
                },
                'value': result.name,
            } for result in context['object_list']
        ]

class BatchView(LoginRequiredMixin, FormView):
    template_name = 'brew/batch/batch.html'
    batch = None
    form_class = None

    def dispatch(self, request, *args, **kwargs):
        batch_id = kwargs.get("pk", None)
        if batch_id is None:
            self.batch = None
        else:
            self.batch = Batch.objects.get(pk=batch_id)
        # Attach the request to "self" so "form_valid()" can access it below.
        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BatchView, self).get_context_data(**kwargs)
        context["batch"] = self.batch
        return context

    def form_valid(self, form):
        current_stage = form.cleaned_data.get("stage")
        # Get the next stage after this one.
        previous_stage = False
        if "next_stage" in form.data:
            new_stage = BATCH_STAGE_ORDER[BATCH_STAGE_ORDER.index(current_stage)+1]
        elif "previous_stage" in form.data:
            previous_stage = True
            try:
                new_stage = BATCH_STAGE_ORDER[BATCH_STAGE_ORDER.index(current_stage)-1]
            except IndexError:
                new_stage = BATCH_STAGE_ORDER[0]
        elif "save" in form.data:
            new_stage = current_stage
        elif "finish" in form.data:
            new_stage = "FINISHED"
        form.instance.stage = new_stage
        form.instance.user = self.request.user
        if not previous_stage:
            form.save()  # This will save the underlying instance.
        else:
            form.instance.save()
        if new_stage == "FINISHED":
            return redirect(reverse("brew:batch-detail"))
        # else
        return redirect(reverse("brew:batch-update", args=[form.instance.pk]))

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid() or "previous_stage" in form.data:
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        raise

    def get_form_class(self):
        stage = self.batch.stage if self.batch else "INIT"
        # Get the form fields appropriate to that stage.
        fields = Batch.get_fields_by_stage(stage)
        # Use those fields to dynamically create a form with "modelform_factory"
        return modelform_factory(Batch, BaseBatchForm, fields)
    
    def get_form_kwargs(self):
        # Make sure Django uses the same Batch instance we've already been
        # working on. Otherwise it will instantiate a new one after every submit.
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.batch
        kwargs.update({'request': self.request})
        return kwargs


class FermentableListView(LoginRequiredMixin, ListView):
    model = Fermentable
    template_name = "brew/fermentable/list.html"
    context_object_name = 'fermentables'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(FermentableListView, self).get_context_data(**kwargs)
        fermentables = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(fermentables, self.paginate_by)
        try:
            fermentables = paginator.page(page)
        except PageNotAnInteger:
            fermentables = paginator.page(1)
        except EmptyPage:
            fermentables = paginator.page(paginator.num_pages)
        context['fermentables'] = fermentables
        context['user'] = User.objects.get(id=self.request.user.id)
        context['filter'] = filters.FermentableFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_hops = filters.FermentableFilter(self.request.GET, queryset=qs)
        return filtered_hops.qs


class FermentableCreateView(LoginRequiredMixin, StaffRequiredMixin, BSModalCreateView):
    template_name = 'brew/fermentable/create.html'
    form_class = FermentableModelForm
    success_message = 'Fermentable was successfully created.'
    success_url = reverse_lazy('brew:fermentable-list')


class FermentableDetailView(LoginRequiredMixin, BSModalReadView):
    model = Fermentable
    template_name = 'brew/fermentable/detail.html'
    context_object_name = 'fermentable'


class FermentableUpdateView(LoginRequiredMixin, StaffRequiredMixin, BSModalUpdateView):
    model = Fermentable
    form_class = FermentableModelForm
    template_name = 'brew/fermentable/update.html'
    success_message = 'Success: Fermentable was updated.'
    context_object_name = 'fermentable'
    success_url = reverse_lazy('brew:fermentable-list')


class FermentableDeleteView(LoginRequiredMixin, StaffRequiredMixin, BSModalDeleteView):
    model = Fermentable
    template_name = 'brew/fermentable/delete.html'
    success_message = 'Fermentable was deleted.'
    success_url = reverse_lazy('brew:fermentable-list')

#
# HOPS
#

class HopListView(LoginRequiredMixin, ListView):
    model = Hop
    template_name = "brew/hop/list.html"
    context_object_name = 'hops'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(HopListView, self).get_context_data(**kwargs)
        hops = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(hops, self.paginate_by)
        try:
            hops = paginator.page(page)
        except PageNotAnInteger:
            hops = paginator.page(1)
        except EmptyPage:
            hops = paginator.page(paginator.num_pages)
        context['hops'] = hops
        context['user'] = User.objects.get(id=self.request.user.id)
        context['filter'] = filters.HopFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_hops = filters.HopFilter(self.request.GET, queryset=qs)
        return filtered_hops.qs


class HopCreateView(LoginRequiredMixin, StaffRequiredMixin, BSModalCreateView):
    template_name = 'brew/hop/create.html'
    form_class = HopModelForm
    success_message = 'Hop was successfully created.'
    success_url = reverse_lazy('brew:hop-list')


class HopDetailView(LoginRequiredMixin, BSModalReadView):
    model = Hop
    template_name = 'brew/hop/detail.html'
    context_object_name = 'hop'


class HopUpdateView(LoginRequiredMixin, StaffRequiredMixin, BSModalUpdateView):
    model = Hop
    form_class = HopModelForm
    template_name = 'brew/hop/update.html'
    success_message = 'Success: Hop was updated.'
    context_object_name = 'hop'
    success_url = reverse_lazy('brew:hop-list')


class HopDeleteView(LoginRequiredMixin, StaffRequiredMixin, BSModalDeleteView):
    model = Hop
    template_name = 'brew/hop/delete.html'
    success_message = 'Hop was deleted.'
    success_url = reverse_lazy('brew:hop-list')


#
# YEAST
#
class YeastListView(LoginRequiredMixin, ListView):
    model = Yeast
    template_name = "brew/yeast/list.html"
    context_object_name = 'yeasts'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(YeastListView, self).get_context_data(**kwargs)
        yeasts = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(yeasts, self.paginate_by)
        try:
            yeasts = paginator.page(page)
        except PageNotAnInteger:
            yeasts = paginator.page(1)
        except EmptyPage:
            yeasts = paginator.page(paginator.num_pages)
        context['yeasts'] = yeasts
        context['user'] = User.objects.get(id=self.request.user.id)
        context['filter'] = filters.YeastFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_yeasts = filters.YeastFilter(self.request.GET, queryset=qs)
        return filtered_yeasts.qs


class YeastCreateView(LoginRequiredMixin, StaffRequiredMixin, BSModalCreateView):
    template_name = 'brew/yeast/create.html'
    form_class = YeastModelForm
    success_message = 'Yeast was successfully created.'
    success_url = reverse_lazy('brew:yeast-list')


class YeastDetailView(LoginRequiredMixin, BSModalReadView):
    model = Yeast
    template_name = 'brew/yeast/detail.html'
    context_object_name = 'yeast'


class YeastUpdateView(LoginRequiredMixin, StaffRequiredMixin, BSModalUpdateView):
    model = Yeast
    form_class = YeastModelForm
    template_name = 'brew/yeast/update.html'
    success_message = 'Success: Yeast was updated.'
    context_object_name = 'yeast'
    success_url = reverse_lazy('brew:yeast-list')


class YeastDeleteView(LoginRequiredMixin, StaffRequiredMixin, BSModalDeleteView):
    model = Yeast
    template_name = 'brew/yeast/delete.html'
    success_message = 'Yeast was deleted.'
    success_url = reverse_lazy('brew:yeast-list')


#
# Extra
#
class ExtraListView(LoginRequiredMixin, ListView):
    model = Extra
    template_name = "brew/extra/list.html"
    context_object_name = 'extras'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ExtraListView, self).get_context_data(**kwargs)
        extras = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(extras, self.paginate_by)
        try:
            extras = paginator.page(page)
        except PageNotAnInteger:
            extras = paginator.page(1)
        except EmptyPage:
            extras = paginator.page(paginator.num_pages)
        context['extras'] = extras
        context['user'] = User.objects.get(id=self.request.user.id)
        context['filter'] = filters.ExtraFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_extras = filters.ExtraFilter(self.request.GET, queryset=qs)
        return filtered_extras.qs


class ExtraCreateView(LoginRequiredMixin, StaffRequiredMixin, BSModalCreateView):
    template_name = 'brew/extra/create.html'
    form_class = ExtraModelForm
    success_message = 'Extra was successfully created.'
    success_url = reverse_lazy('brew:extra-list')


class ExtraDetailView(LoginRequiredMixin, BSModalReadView):
    model = Extra
    template_name = 'brew/extra/detail.html'
    context_object_name = 'extra'


class ExtraUpdateView(LoginRequiredMixin, StaffRequiredMixin, BSModalUpdateView):
    model = Extra
    form_class = ExtraModelForm
    template_name = 'brew/extra/update.html'
    success_message = 'Success: Extra was updated.'
    context_object_name = 'extra'
    success_url = reverse_lazy('brew:extra-list')


class ExtraDeleteView(LoginRequiredMixin, StaffRequiredMixin, BSModalDeleteView):
    model = Extra
    template_name = 'brew/extra/delete.html'
    success_message = 'Extra was deleted.'
    success_url = reverse_lazy('brew:extra-list')


#
# Style
#
class StyleListView(LoginRequiredMixin, ListView):
    model = Style
    template_name = "brew/style/list.html"
    context_object_name = 'styles'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(StyleListView, self).get_context_data(**kwargs)
        styles = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(styles, self.paginate_by)
        try:
            styles = paginator.page(page)
        except PageNotAnInteger:
            styles = paginator.page(1)
        except EmptyPage:
            styles = paginator.page(paginator.num_pages)
        context['styles'] = styles
        context['user'] = User.objects.get(id=self.request.user.id)
        context['filter'] = filters.StyleFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.all()
        filtered_styles = filters.StyleFilter(self.request.GET, queryset=qs)
        return filtered_styles.qs


class StyleCreateView(LoginRequiredMixin, StaffRequiredMixin, BSModalCreateView):
    template_name = 'brew/style/create.html'
    form_class = StyleModelForm
    success_message = 'Style was successfully created.'
    success_url = reverse_lazy('brew:style-list')


class StyleDetailView(LoginRequiredMixin, BSModalReadView):
    model = Style
    template_name = 'brew/style/detail.html'
    context_object_name = 'style'


class StyleInfoView(LoginRequiredMixin, BSModalReadView):
    http_method_allowed = ('GET', 'POST')
    model = Style
    context_object_name = 'style'

    def get_context_data(self, **kwargs):
        context = super(StyleInfoView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context):
        """Return a JSON response in correct format."""
        if self.request.user.profile.gravity_units.lower() == "plato":
            gprec = 1
        else:
            gprec = 4
        return JsonResponse(
            {
                'name': context["style"].name,
                "og_min": f'{round(getattr(context["style"].og_min, self.request.user.profile.gravity_units.lower()), gprec)}',
                "og_max": f'{round(getattr(context["style"].og_max, self.request.user.profile.gravity_units.lower()), gprec)}',
                "fg_min": f'{round(getattr(context["style"].fg_min, self.request.user.profile.gravity_units.lower()), gprec)}',
                "fg_max": f'{round(getattr(context["style"].fg_max, self.request.user.profile.gravity_units.lower()), gprec)}',
                "ibu_min": f'{round(float(context["style"].ibu_min), 1)}',
                "ibu_max": f'{round(float(context["style"].ibu_max), 1)}',
                "color_min": f'{round(getattr(context["style"].color_min, self.request.user.profile.color_units.lower()), 1)}',
                "color_max": f'{round(getattr(context["style"].color_max, self.request.user.profile.color_units.lower()), 1)}',
                "alcohol_min": f'{round(float(context["style"].alcohol_min), 1)}',
                "alcohol_max": f'{round(float(context["style"].alcohol_max), 1)}'
            })


class StyleUpdateView(LoginRequiredMixin, StaffRequiredMixin, BSModalUpdateView):
    model = Style
    form_class = StyleModelForm
    template_name = 'brew/style/update.html'
    success_message = 'Success: Style was updated.'
    context_object_name = 'style'
    success_url = reverse_lazy('brew:style-list')


class StyleDeleteView(LoginRequiredMixin, StaffRequiredMixin, BSModalDeleteView):
    model = Style
    template_name = 'brew/style/delete.html'
    success_message = 'Style was deleted.'
    success_url = reverse_lazy('brew:style-list')


#
# Recipes
#
class RecipeListView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "brew/recipe/list.html"
    context_object_name = 'recipes'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        recipes = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(recipes, self.paginate_by)
        try:
            recipes = paginator.page(page)
        except PageNotAnInteger:
            recipes = paginator.page(1)
        except EmptyPage:
            recipes = paginator.page(paginator.num_pages)
        context['recipes'] = recipes
        context['user'] = User.objects.get(id=self.request.user.id)
        context['filter'] = filters.RecipeFilter(self.request.GET)
        return context

    def get_queryset(self):
        qs = self.model.objects.filter(user=self.request.user)
        filtered_recipes = filters.RecipeFilter(self.request.GET, queryset=qs)
        return filtered_recipes.qs


class RecipeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'brew/recipe/create.html'
    form_class = RecipeModelForm
    success_message = 'Recipe was successfully created.'
    success_url = reverse_lazy('brew:recipe-list')

    def get_form_kwargs(self):
        kwargs = super(RecipeCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(RecipeCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['fermentables'] = forms.FermentableIngredientFormSet(self.request.POST, request=self.request)
            data['hops'] = forms.HopIngredientFormSet(self.request.POST, request=self.request)
            data['yeasts'] = forms.YeastIngredientFormSet(self.request.POST, request=self.request)
            #data['extras'] = forms.ExtraIngredientFormSet(self.request.POST, request=self.request)
            data['mash_steps'] = forms.MashStepFormSet(self.request.POST, request=self.request)
        else:
            data['fermentables'] = forms.FermentableIngredientFormSet(request=self.request)
            data['hops'] = forms.HopIngredientFormSet(request=self.request)
            data['yeasts'] = forms.YeastIngredientFormSet(request=self.request)
            #data['extras'] = forms.ExtraIngredientFormSet(request=self.request)
            data['mash_steps'] = forms.MashStepFormSet(request=self.request)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fermentables = context['fermentables']
        hops = context['hops']
        #extras = context['extras']
        yeasts = context['yeasts']
        mash_steps = context['mash_steps']
        formsets = [fermentables, hops, yeasts, mash_steps]
        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            for formset in formsets:
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()
        return super(RecipeCreateView, self).form_valid(form)


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'brew/recipe/create.html'
    form_class = RecipeModelForm
    success_message = 'Recipe was successfully created.'
    success_url = reverse_lazy('brew:recipe-list')
    model = Recipe

    def get_form_kwargs(self):
        kwargs = super(RecipeUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(RecipeUpdateView, self).get_context_data(**kwargs)
        units = _get_units_for_user(self.request.user)
        data.update(units)

        if self.request.POST:
            data['fermentables'] = forms.FermentableIngredientFormSet(self.request.POST, request=self.request, instance=self.object)
            data['hops'] = forms.HopIngredientFormSet(self.request.POST, request=self.request, instance=self.object)
            data['yeasts'] = forms.YeastIngredientFormSet(self.request.POST, request=self.request, instance=self.object)
            #data['extras'] = forms.ExtraIngredientFormSet(self.request.POST, request=self.request, instance=self.object)
            data['mash_steps'] = forms.MashStepFormSet(self.request.POST, request=self.request, instance=self.object)
        else:
            data['fermentables'] = forms.FermentableIngredientFormSet(request=self.request, instance=self.object)
            data['hops'] = forms.HopIngredientFormSet(request=self.request, instance=self.object)
            data['yeasts'] = forms.YeastIngredientFormSet(request=self.request, instance=self.object)
            #data['extras'] = forms.ExtraIngredientFormSet(request=self.request, instance=self.object)
            data['mash_steps'] = forms.MashStepFormSet(request=self.request, instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        fermentables = context['fermentables']
        hops = context['hops']
        #extras = context['extras']
        yeasts = context['yeasts']
        mash_steps = context['mash_steps']
        formsets = [fermentables, hops, yeasts, mash_steps]
        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            for formset in formsets:
                if formset.is_valid():
                    formset.instance = self.object
                    formset.save()
        return super(RecipeUpdateView, self).form_valid(form)


class RecipeDetailView(LoginRequiredMixin, BSModalReadView):
    model = Recipe
    template_name = 'brew/recipe/detail.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        data = super(RecipeDetailView, self).get_context_data(**kwargs)
        units = _get_units_for_user(self.request.user)
        data.update(units)
        return data


class RecipeDeleteView(LoginRequiredMixin, StaffRequiredMixin, BSModalDeleteView):
    model = Recipe
    template_name = 'brew/recipe/delete.html'
    success_message = 'Recipe was deleted.'
    success_url = reverse_lazy('brew:recipe-list')


class RecipePrintView(WeasyTemplateResponseMixin, RecipeDetailView):
    # pdf_stylesheets = [
    #     static('/css/bootstrap.min.css'),
    #     static('/fontawesome_free/css/all.min.css'),
    #     static('/css/project.css'),
    # ]
    template_name = 'brew/recipe/print.html'
    pdf_attachment = False