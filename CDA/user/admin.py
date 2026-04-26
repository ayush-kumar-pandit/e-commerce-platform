from django.contrib import admin
from .models import UserProfile, Cart, CartItem

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)
