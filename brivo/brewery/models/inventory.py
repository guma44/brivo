from django.db import models
from django.utils.translation import gettext_lazy as _

from brivo.brewery.models import BaseModel

__all__ = ("Inventory",)

class Inventory(models.Model):
    user = models.OneToOneField("users.User", verbose_name=_("brewery.User"), on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.user.username} Inventory"
