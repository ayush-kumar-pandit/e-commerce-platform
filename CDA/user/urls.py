from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name = 'register'),
    path('verify-otp/', verify_otp_view, name = 'verify_otp'),
    path('login/', login_view, name = 'login'),
    path('logout/', logout_view, name = 'logout'),
    path('profile/', profile_view, name = 'profile'),
    path('cart_view/', cart_view, name = 'cart_view'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/<str:action>/', update_cart_item, name='update_cart_item'),
    path('remove-cart/<int:item_id>/', remove_cart_item, name='remove_cart_item'),
    path('change-password/', change_password_view, name='change_password'),
]
