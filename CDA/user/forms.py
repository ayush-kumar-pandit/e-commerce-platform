from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class UserLoginForm(forms.Form):
    credential = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or phone number', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
        label="Email or Phone Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
        label="Password"
    )
