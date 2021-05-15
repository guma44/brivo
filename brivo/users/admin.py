from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from brivo.users.forms import AdminUserChangeForm, AdminUserCreationForm
from brivo.users.models import UserProfile, UserBrewery
from brivo.brewery import models

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    list_display = ('email', 'username', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                ),
            },
        ),
        (_("Important dates"), {"fields": ()}),
    )
    search_fields = ("email", "username")
    ordering = ("email",)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password")
        }),
    )
    filter_horizontal = ()

admin.site.register(UserProfile)
admin.site.register(UserBrewery)
admin.site.register(models.Fermentable)
admin.site.register(models.Hop)
admin.site.register(models.Yeast)
admin.site.register(models.Extra)
admin.site.register(models.IngredientFermentable)
admin.site.register(models.IngredientHop)
admin.site.register(models.IngredientYeast)
admin.site.register(models.IngredientExtra)
admin.site.register(models.MashStep)
admin.site.register(models.Recipe)