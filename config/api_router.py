from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from brivo.users.api.views import UserViewSet
from brivo.brewery.api import views as brewery_views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("brewery/hops", brewery_views.HopViewSet)
router.register("brewery/fermentables", brewery_views.FermentableViewSet)
router.register("brewery/extras", brewery_views.ExtraViewSet)
router.register("brewery/yeasts", brewery_views.YeastViewSet)
router.register("brewery/styles", brewery_views.StyleViewSet)
router.register("brewery/recipes", brewery_views.RecipeViewSet)
router.register("brewery/batches", brewery_views.BatchViewSet)
router.register("brewery/calc", brewery_views.BeerCalculatorViewSet, "Calculator")

app_name = "api"
urlpatterns = router.urls
