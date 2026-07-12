from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import re


class PasswordStrengthValidator:
    """
    Validator to enforce strong password requirements:
    - Minimum 8 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one digit (0-9)
    - At least one special character (!@#$%^&*)
    """
    
    def validate(self, password):
        """
        Validate password strength and return list of errors if any.
        """
        errors = []
        
        # Check minimum length
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        
        # Check for uppercase letters
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter (A-Z).")
        
        # Check for lowercase letters
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter (a-z).")
        
        # Check for digits
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number (0-9).")
        
        # Check for special characters
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append("Password must contain at least one special character (!@#$%^&*).")
        
        return errors


class UserRegistrationForm(forms.ModelForm):
    full_name = forms.CharField(
        required=True,
        error_messages={'required': 'Full Name cannot be empty.'},
        widget=forms.TextInput(attrs={'placeholder': 'Enter full name', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700', 'required': 'required'})
        ,
        label="Full Name"
    )
    password = forms.CharField(
        required=True,
        error_messages={'required': 'Password cannot be empty.'},
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter strong password',
            'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700',
            'required': 'required'
        }),
        help_text='<small class="text-gray-600">Password must contain: at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character (!@#$%^&*).</small>'
    )
    confirm_password = forms.CharField(
        required=True,
        error_messages={'required': 'Please confirm your password.'},
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700', 'required': 'required'})
    )

    class Meta:
        model = User
        fields = ['full_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700', 'required': 'required'})
        }
        error_messages = {
            'email': {'required': 'Email cannot be empty.'},
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise forms.ValidationError('Full Name cannot be empty.')
        if len(full_name) < 2:
            raise forms.ValidationError('Full Name must be at least 2 characters long.')
        return full_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise forms.ValidationError('Email cannot be empty.')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '').strip()
        if not password:
            raise forms.ValidationError('Password cannot be empty.')
        
        # Validate password strength
        validator = PasswordStrengthValidator()
        errors = validator.validate(password)
        
        if errors:
            # Combine all errors into one message
            error_message = 'Password does not meet security requirements:\n' + '\n'.join(errors)
            raise forms.ValidationError(error_message)
        
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password', '').strip()
        if not confirm_password:
            raise forms.ValidationError('Please confirm your password.')
        return confirm_password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=False):
        """
        IMPORTANT: commit=False by default to prevent saving users before email verification.
        The user is only saved after OTP verification in verify_otp_view().
        """
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('full_name', '')
        
        # Auto-generate a unique username based on email
        email = self.cleaned_data.get('email', '')
        base_username = email.split('@')[0] if '@' in email else 'user'
        import uuid
        user.username = f"{base_username}_{uuid.uuid4().hex[:6]}"
        
        # Never save during registration form — only return user object
        return user


class UserLoginForm(forms.Form):
    credential = forms.CharField(
        required=True,
        error_messages={'required': 'Email or phone number cannot be empty.'},
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or phone number', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700', 'required': 'required'})
        ,
        label="Email or Phone Number"
    )
    password = forms.CharField(
        required=True,
        error_messages={'required': 'Password cannot be empty.'},
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'w-full border border-gray-300 rounded px-4 py-3 focus:outline-none focus:border-green-700', 'required': 'required'})
        ,
        label="Password"
    )

    def clean_credential(self):
        credential = self.cleaned_data.get('credential', '').strip()
        if not credential:
            raise forms.ValidationError('Email or phone number cannot be empty.')
        return credential

    def clean_password(self):
        password = self.cleaned_data.get('password', '').strip()
        if not password:
            raise forms.ValidationError('Password cannot be empty.')
        return password
