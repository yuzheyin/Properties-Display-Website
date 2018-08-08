from django import forms
from .models import *
from .choices import *

MAX_UPLOAD_SIZE = 5000000


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)

    last_name  = forms.CharField(max_length=20)
    email      = forms.CharField(max_length=50,
                                 widget = forms.EmailInput())
    username   = forms.CharField(max_length = 20)
    password1  = forms.CharField(max_length = 200,
                                 label='Password',
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200,
                                 label='Confirm password',
                                 widget = forms.PasswordInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    latitude = forms.FloatField(widget=forms.HiddenInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("Email is already used.")
        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username


class FilterForm(forms.Form):
    keyword = forms.CharField(max_length=100, label="Keyword")
    city = forms.ChoiceField(choices=CITY_CHOICES, label="City", required=False)
    state = forms.ChoiceField(choices=STATE_CHOICES, label="State", required=False)


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        }
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Please confirm the passwords you entered.")
        return password2