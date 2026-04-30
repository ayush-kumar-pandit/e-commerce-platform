from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter full name', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}), label="Full Name")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}))

    class Meta:
        model = User
        fields = ['full_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
        }

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('full_name', '')
        
        # Auto-generate a unique username based on email
        email = self.cleaned_data.get('email', '')
        base_username = email.split('@')[0] if '@' in email else 'user'
        import uuid
        user.username = f"{base_username}_{uuid.uuid4().hex[:6]}"
        
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    credential = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or phone number', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
        label="Email or Phone Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700'}),
        label="Password"
    )
