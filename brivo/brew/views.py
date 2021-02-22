import datetime, pytz
from django.utils.decorators import method_decorator
from django.forms import modelform_factory
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from . import constants
from brivo.brew.forms import BaseBatchForm
from brivo.brew.models import Batch, BATCH_STAGE_ORDER, Fermentable


class BatchView(FormView):
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


class FermentableListView(ListView):
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
        return context


# @method_decorator(login_required, name='dispatch')
class FermentableCreateView(CreateView):
    model = Fermentable
    template_name = 'brew/fermentable/create.html'
    fields = "__all__"
    success_url = reverse_lazy('brew:fermentable-list')


# @method_decorator(login_required, name='dispatch')
class FermentableDetailView(DetailView):

    model = Fermentable
    template_name = 'brew/fermentable/detail.html'
    context_object_name = 'fermentable'


# @method_decorator(login_required, name='dispatch')
class FermentableUpdateView(UpdateView):

    model = Fermentable
    template_name = 'brew/fermentable/update.html'
    context_object_name = 'fermentable'
    fields = "__all__"

    def get_success_url(self):
        return reverse_lazy('brew:fermentable-detail', kwargs={'pk': self.object.id})


# @method_decorator(login_required, name='dispatch')
class FermentableDeleteView(DeleteView):
    model = Fermentable
    template_name = 'brew/fermentable/delete.html'
    success_url = reverse_lazy('brew:fermentable-list')