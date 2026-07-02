from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('our-science/', our_science_view, name='our_science'),
]
