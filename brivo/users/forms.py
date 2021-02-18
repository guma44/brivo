from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from allauth.account.forms import SignupForm

from brivo.users.models import (
    GENERAL_UNITS,
    GRAVITY_UNITS,
    UserProfile,
    BreweryProfile)


User = get_user_model()


class AdminUserCreationForm(admin_forms.UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)


    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ('email', 'username')
        error_messages = {
            "email": {"unique": _("This email has already been registered.")},
            "username": {"unique": _("This username has already been taken.")},
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        profile = UserProfile.objects.create(user=user).save()
        brewery_profile = BreweryProfile.objects.create(user=user).save()
        if commit:
            user.save()
        return user


class AdminUserChangeForm(admin_forms.UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'password', 'is_active', 'is_staff')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class BrivoSignupForm(SignupForm):

    general_units = forms.ChoiceField(choices=GENERAL_UNITS, required=False)
    gravity_units = forms.ChoiceField(choices=GRAVITY_UNITS, required=False)

    # Override the init method
    def __init__(self, *args, **kwargs):
        # Call the init of the parent class
        super().__init__(*args, **kwargs)

    # Put in custom signup logic
    def custom_signup(self, request, user):
        print("Setting data")
        user.profile = UserProfile.objects.create(user=user)
        user.profile.general_units = self.cleaned_data["general_units"]
        user.profile.gravity_units = self.cleaned_data["gravity_units"]
        user.brewery_profile = BreweryProfile.objects.create(user=user)
        user.brewery_profile.save()
        user.profile.save()
        user.save()


# class UserForm(forms.ModelForm):
#     """A form for updating users. Includes all the fields on
#     the user, but replaces the password field with admin's
#     password hash display field.
#     """

#     class Meta:
#         model = User
#         fields = ('username', 'email',)


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = (
#             "image",
#             "general_units",
#             "temperature_units",
#             "gravity_units",
#             "color_units",
#             "ibu_type"
#         )


# class BreweryProfileForm(forms.ModelForm):
    
#     class Meta:
#         model = BreweryProfile
#         fields = (
#             "image",
#             "name",
#             "external_link",
#             "number_of_batches"
#         )

