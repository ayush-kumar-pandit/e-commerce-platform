from django.shortcuts import render
from .models import Product, OurScience

# Create your views here.
def home(request):
    prods = Product.objects.all()
    return render(request,"home.html", {"prods": prods})

def about_view(request):
    return render(request, "about.html")

def contact_view(request):
    return render(request, "contact.html")

def our_science_view(request):
    # Fetch the first OurScience object, or None if it doesn't exist yet
    science_data = OurScience.objects.first()
    return render(request, "our_science.html", {"science_data": science_data})