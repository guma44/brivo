from django.urls import path
from django.views import defaults as default_views

from brivo.users.views import (
    user_redirect_view,
    user_settings_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("<str:username>/", view=user_settings_view, name="settings"),
]
