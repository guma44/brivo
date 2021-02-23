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
]