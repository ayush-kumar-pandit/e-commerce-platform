from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # The 'username' argument could be email, phone number, or the actual username
        credential = kwargs.get('email') or kwargs.get('phone') or username
        if not credential:
            return None

        user_obj = None
        
        # Try to find user by email
        user_obj = User.objects.filter(email=credential).first()

        # Try to find user by phone number via UserProfile
        if not user_obj:
            try:
                profile = UserProfile.objects.filter(phone=credential).first()
                if profile:
                    user_obj = profile.user
            except Exception:
                pass

        if user_obj and user_obj.check_password(password) and self.user_can_authenticate(user_obj):
            return user_obj
        return None
