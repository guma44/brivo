from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, RedirectView, UpdateView
from brivo.users.models import UserProfile, UserBrewery
from brivo.users import forms

User = get_user_model()

def user_settings_view(request, username):
    if not request.user.is_authenticated:
        return render(request, "403.html")
    if username != request.user.username:
        return render(request, "404.html")
    user = request.user
    user_profile = user.profile
    user_brewery = user.brewery_profile
    user_form = forms.UserForm(instance=request.user)
    

    if request.method == "POST":
        if 'profile_form' in request.POST:
            profile_form = forms.UserProfileForm(request.POST, request.FILES, instance=user.profile)
            if profile_form.is_valid():
                profile_form.save()

        if 'user_form' in request.POST:
            user_form = forms.UserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()

        if 'brewery_form' in request.POST:
            brewery_form = forms.UserBreweryForm(request.POST, request.FILES, instance=user.brewery_profile)
            if brewery_form.is_valid():
                brewery_form.save()

    if user_profile:
        profile_form = forms.UserProfileForm(instance=user_profile)
    else:
        profile_form = forms.UserProfileForm()
    if user_brewery:
        brewery_form = forms.UserBreweryForm(instance=user_brewery)
    else:
        brewery_form = forms.UserBreweryForm()
    return render(request, 'users/settings.html', {
        'profile_form': profile_form,
        'user_form': user_form,
        'brewery_form': brewery_form
    })


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:settings", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
