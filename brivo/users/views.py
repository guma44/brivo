from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from brivo.users.models import UserProfile, BreweryProfile

User = get_user_model()

class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    fields = ["username", "email"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = UserProfile
    fields = (
        "image",
        "general_units",
        "temperature_units",
        "gravity_units",
        "color_units"
    )
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)


class BreweryProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = BreweryProfile
    fields = (
        "image",
        "name",
        "external_link",
        "number_of_batches"
    )
    success_message = _("Information successfully updated")

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return BreweryProfile.objects.get(user=self.request.user)


user_update_view = UserUpdateView.as_view()
userprofile_update_view = UserProfileUpdateView.as_view()
brewery_update_view = BreweryProfileUpdateView.as_view()

class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
