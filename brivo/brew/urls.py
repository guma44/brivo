from django.urls import path

from . import views

app_name = "brew"
urlpatterns = [
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
]