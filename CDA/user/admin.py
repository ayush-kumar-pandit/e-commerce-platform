from django.contrib import admin
from .models import UserProfile, Cart, CartItem
from django.utils.html import format_html

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'user_email', 'phone', 'image_preview']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Profile Image'

# Register your models here.
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
