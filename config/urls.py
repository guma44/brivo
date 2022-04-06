from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.utils import translation
from django.urls import include, path, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from brivo.users.api.views import CustomLogoutView

def set_language_from_url(request, user_language):
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return redirect(request.META.get('HTTP_REFERER'))

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management

    re_path(r'^celery-progress/', include('celery_progress.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router", namespace="api")),
    path("api/auth/logout/", CustomLogoutView.as_view()),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
        path(r'/set_language/(?P<user_language>\w+)/$', set_language_from_url, name="set_language_from_url"),
        path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
        path(
            "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
        ),
        path("users/", include("brivo.users.urls", namespace="users")),
        path("brewery/", include("brivo.brewery.urls", namespace="brewery")),
        path("accounts/email/", default_views.page_not_found, name="account_email", kwargs={"exception": Exception("Page not Found")},),
        path("accounts/", include("allauth.urls")),
    )


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
