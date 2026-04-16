from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_view, name = 'register'),
    path('login/', login_view, name = 'login'),
    path('logout/', logout_view, name = 'logout'),
    path('profile/', profile_view, name = 'profile'),
    path('cart_view/', cart_view, name = 'cart_view'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),


]
