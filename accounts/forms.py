from django import forms
from django.contrib.auth import get_user_model
from accounts.models import Account
from django.db.utils import IntegrityError

USER_MODEL = get_user_model()


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=200)
    email = forms.EmailField(max_length=254)
    profile_pic = forms.ImageField(required=False)
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput())

    def clean_username(self):
        if USER_MODEL.objects.filter(username=self.cleaned_data.get("username")).exists():
            raise forms.ValidationError("Username is not available")

        return self.cleaned_data.get("username")

    def clean(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if (not password1) or (password1 != password2):
            raise forms.ValidationError("Passwords are not the same")
        super(SignupForm, self).clean()

        return self.cleaned_data
    
    def create_user_method(self):
        data = self.cleaned_data

        user = USER_MODEL()
        account = Account()

        user.first_name = data.get("first_name")
        user.last_name = data.get("last_name")
        user.username = data.get("username")
        user.email = data.get("email")
        user.set_password(data.get("password1"))
        user.save()
        account.user = user
        if data.get("profile_picture"):
            account.profile_picture = data.get("profile_picture")
        account.save()

    def is_valid(self, *args, **kwargs):
        valid = super().is_valid()

        if valid:
            self.create_user_method()
        return valid


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput())
