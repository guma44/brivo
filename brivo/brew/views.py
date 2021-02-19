import datetime, pytz
from django.forms import modelform_factory
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from . import constants
from .forms import BaseBatchForm
from .models import Batch, BATCH_STAGE_ORDER


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