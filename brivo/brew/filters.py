from brivo.brew import models

import django_filters

class HopFilter(django_filters.FilterSet):

    alpha_acids__gt = django_filters.NumberFilter(field_name='alpha_acids', lookup_expr='gt')
    alpha_acids__lt = django_filters.NumberFilter(field_name='alpha_acids', lookup_expr='lt')
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.Hop
        fields = ["name", "type", "country"]


class FermentableFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    color__gt = django_filters.NumberFilter(field_name='color', lookup_expr='gt')
    color__lt = django_filters.NumberFilter(field_name='color', lookup_expr='lt')

    class Meta:
        model = models.Fermentable
        fields = ["name", "type"]


class YeastFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    lab = django_filters.CharFilter(field_name="lab", lookup_expr="icontains")

    class Meta:
        model = models.Yeast
        fields = ["name", "type", "form", "lab"]


class ExtraFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.Extra
        fields = ["name", "type", "use"]


class StyleFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category", lookup_expr="icontains")

    class Meta:
        model = models.Style
        fields = ["name", "category", "ferm_type"]


class RecipeFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = models.Recipe
        fields = ["name"]