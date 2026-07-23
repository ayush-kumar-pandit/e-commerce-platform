from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile


class EmailUsernamePhoneBackend(ModelBackend):
    """
    Custom authentication backend that allows login via:
    - Email address
    - Username
    - Phone number (via UserProfile)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email, username, or phone number.
        The 'username' argument can be email, phone, or actual username.
        """
        if not username or not password:
            return None
        
        credential = username.strip()
        user_obj = None
        
        # Try to find user by username first
        user_obj = User.objects.filter(username=credential).first()
        
        # Try to find user by email
        if not user_obj:
            user_obj = User.objects.filter(email=credential).first()
        
        # Try to find user by phone number via UserProfile
        if not user_obj:
            try:
                profile = UserProfile.objects.filter(phone=credential).first()
                if profile:
                    user_obj = profile.user
            except Exception:
                pass
        
        # Verify password and user is active
        if user_obj and user_obj.check_password(password) and self.user_can_authenticate(user_obj):
            return user_obj
        
        return None
