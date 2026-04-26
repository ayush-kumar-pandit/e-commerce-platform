from django.shortcuts import render
from .models import Product

# Create your views here.
def home(request):
    prods = Product.objects.all()
    return render(request,"home.html", {"prods": prods})

def about_view(request):
    return render(request, "about.html")

def contact_view(request):
    return render(request, "contact.html")