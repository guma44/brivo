import os
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _



GENERAL_UNITS = (
    ('METRIC', 'Metric'),
    ('IMPERIAL', 'Imperial')
)

TEMPERATURE_UNITS = (
    ('CELSIUS', 'Celsius'),
    ('KELVIN', 'Kelvin'),
    ('FAHRENHEIT', 'Fahrenheit')
)

GRAVITY_UNITS = (
    ('PLATO', 'Plato'),
    ('SG', 'SG')
)

COLOR_UNITS = (
    ('SRM', 'SRM'),
    ('EBC', 'EBC')
)


def user_profile_image_file_path(instance, filename):
    """Generate filepath for new user_profile image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/user_profile/", filename)


def brewery_profile_image_file_path(instance, filename):
    """Generate filepath for new brewery_profile image""" 
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/brewery_profile/", filename)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email or email is None:
            raise ValueError("Email is obligatory")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"email": self.email})


class UserProfile(models.Model):
    user = models.OneToOneField("User", verbose_name=_("User"), on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(null=True, upload_to=user_profile_image_file_path, blank=True)
    general_units = models.CharField(_("General Units"), max_length=255, choices=GENERAL_UNITS, default="METRIC")
    temperature_units = models.CharField(_("Temperature Units"), max_length=255, choices=TEMPERATURE_UNITS, default="CELSIUS")
    gravity_units = models.CharField(_("Gravity Units"), max_length=255, choices=GRAVITY_UNITS, default="Plato")
    color_units = models.CharField(_("Color Units"), max_length=255, choices=COLOR_UNITS, default="SRM")


class BreweryProfile(models.Model):
    user = models.OneToOneField("User", verbose_name=_("User"), on_delete=models.CASCADE, related_name="brewery_profile")
    image = models.ImageField(null=True, upload_to=brewery_profile_image_file_path, blank=True)
    name = models.CharField(_("Brewery Name"), max_length=50, blank=True)
    external_link = models.URLField(_("External URL"), max_length=200, blank=True)
    number_of_batches = models.IntegerField(_("Number of Batches"), default=0)
