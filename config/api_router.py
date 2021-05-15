from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from brivo.users.api.views import UserViewSet
from brivo.brewery.api import views as brewery_views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("hops", brewery_views.HopViewSet)
router.register("fermentables", brewery_views.FermentableViewSet)
router.register("extras", brewery_views.ExtraViewSet)
router.register("yeasts", brewery_views.YeastViewSet)
router.register("styles", brewery_views.StyleViewSet)
router.register("recipes", brewery_views.RecipeViewSet)

app_name = "api"
urlpatterns = router.urls
