import datetime, pytz
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
# from . import constants
from brivo.brew.forms import BaseBatchForm, FermentableModelForm, HopModelForm, YeastModelForm, ExtraModelForm
from brivo.brew.models import Batch, BATCH_STAGE_ORDER, Fermentable, Hop, Yeast, Extra
from brivo.users.models import User
from brivo.brew import filters


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class BatchView(LoginRequiredMixin, FormView):
    template_name = 'batch/batch.html'
    batch = None
    form_class = None

    def form_valid(self, form):
        current_stage = form.cleaned_data.get("stage")
        # Get the next stage after this one.
        if "next_stage" in form.data:
            new_stage = BATCH_STAGE_ORDER[BATCH_STAGE_ORDER.index(current_stage)+1]
        elif "previous_stage":
            try:
                new_stage = BATCH_STAGE_ORDER[BATCH_STAGE_ORDER.index(current_stage)-1]
            except IndexError:
                new_stage = BATCH_STAGE_ORDER[0]
        form.instance.stage = new_stage
        form.save()  # This will save the underlying instance.
        if new_stage == constants.COMPLETE:
            return redirect(reverse("batch:finished"))
        # else
        return redirect(reverse("batch:batch"))

    def get_form_class(self):
        stage = self.batch.stage if self.batch.stage else "MASHING"
        # Get the form fields appropriate to that stage.
        fields = Batch.get_fields_by_stage(stage)
        # Use those fields to dynamically create a form with "modelform_factory"
        return modelform_factory(Batch, BaseBatchForm, fields)
    
    def get_form_kwargs(self):
        # Make sure Django uses the same Batch instance we've already been
        # working on. Otherwise it will instantiate a new one after every submit.
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.batch
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