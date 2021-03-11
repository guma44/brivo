from django.urls import path

from . import views

app_name = "brew"
urlpatterns = [
    # Fermentables
    path('fermentable', views.FermentableListView.as_view(),
         name='fermentable-list'),
    path('fermentable/create', views.FermentableCreateView.as_view(),
         name='fermentable-create'),
    path('fermentable/<int:pk>', views.FermentableDetailView.as_view(),
         name='fermentable-detail'),
    path('fermentable/<int:pk>/update', views.FermentableUpdateView.as_view(),
         name='fermentable-update'),
    path('fermentable/<int:pk>/delete', views.FermentableDeleteView.as_view(),
         name='fermentable-delete'),
    path(
        r'fermentable/autocomplete',
        views.FermentableAutocomplete.as_view(),
        name='fermentable-autocomplete',
    ),

    # Hops
    path('hop', views.HopListView.as_view(),
         name='hop-list'),
    path('hop/create', views.HopCreateView.as_view(),
         name='hop-create'),
    path('hop/<int:pk>', views.HopDetailView.as_view(),
         name='hop-detail'),
    path('hop/<int:pk>/update', views.HopUpdateView.as_view(),
         name='hop-update'),
    path('hop/<int:pk>/delete', views.HopDeleteView.as_view(),
         name='hop-delete'),
    path(
        r'hop/autocomplete',
        views.HopAutocomplete.as_view(),
        name='hop-autocomplete',
    ),

    # Yeasts
    path('yeast', views.YeastListView.as_view(),
         name='yeast-list'),
    path('yeast/create', views.YeastCreateView.as_view(),
         name='yeast-create'),
    path('yeast/<int:pk>', views.YeastDetailView.as_view(),
         name='yeast-detail'),
    path('yeast/<int:pk>/update', views.YeastUpdateView.as_view(),
         name='yeast-update'),
    path('yeast/<int:pk>/delete', views.YeastDeleteView.as_view(),
         name='yeast-delete'),
    path(
        r'yeast/autocomplete',
        views.YeastAutocomplete.as_view(),
        name='yeast-autocomplete',
    ),

    # Extras
    path('extra', views.ExtraListView.as_view(),
         name='extra-list'),
    path('extra/create', views.ExtraCreateView.as_view(),
         name='extra-create'),
    path('extra/<int:pk>', views.ExtraDetailView.as_view(),
         name='extra-detail'),
    path('extra/<int:pk>/update', views.ExtraUpdateView.as_view(),
         name='extra-update'),
    path('extra/<int:pk>/delete', views.ExtraDeleteView.as_view(),
         name='extra-delete'),

    # Styles
    path('style', views.StyleListView.as_view(),
         name='style-list'),
    path('style/create', views.StyleCreateView.as_view(),
         name='style-create'),
    path('style/<int:pk>', views.StyleDetailView.as_view(),
         name='style-detail'),
    path('style/<int:pk>/update', views.StyleUpdateView.as_view(),
         name='style-update'),
    path('style/<int:pk>/delete', views.StyleDeleteView.as_view(),
         name='style-delete'),
    path('style/<int:pk>/info', views.StyleInfoView.as_view(),
         name='style-info'),


    # Recipes
    path('recipe', views.RecipeListView.as_view(),
         name='recipe-list'),
    path('recipe/create', views.RecipeCreateView.as_view(),
         name='recipe-create'),
    path('recipe/<int:pk>', views.RecipeDetailView.as_view(),
         name='recipe-detail'),
    path('recipe/<int:pk>/print', views.RecipePrintView.as_view(),
         name='recipe-print'),
    path('recipe/<int:pk>/update', views.RecipeUpdateView.as_view(),
         name='recipe-update'),
    path('recipe/<int:pk>/delete', views.RecipeDeleteView.as_view(),
         name='recipe-delete'),
    path(
        r'recipe/info',
        views.get_recipe_data,
        name='recipe-info',
    ),
]