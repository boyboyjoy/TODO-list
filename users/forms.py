from django import forms
from django.contrib.auth.password_validation import validate_password
from users.models import User


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    moderator = forms.BooleanField(widget=forms.CheckboxInput, required=False)

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']):
            raise forms.ValidationError('That email has taken already')
        return self.cleaned_data['email']

    def clean_password(self):
        validate_password(self.cleaned_data['password'])


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
