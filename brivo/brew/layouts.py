from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from django.shortcuts import render
from django.template.loader import render_to_string

class RecipeFormsetLayout(LayoutObject):

    def __init__(self, formset_name_in_context, template):
        self.formset_name_in_context = formset_name_in_context
        self.fields = []
        self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        for form in formset:
            for field in form:
                field.label = False
        return render_to_string(self.template, {'formset': formset})
