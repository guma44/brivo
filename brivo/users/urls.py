from django.urls import path
from django.views import defaults as default_views

from brivo.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
    userprofile_update_view,
    brewery_update_view
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("~update-profile/", view=userprofile_update_view, name="update-profile"),
    path("~update-brewery/", view=brewery_update_view, name="update-brewery"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
