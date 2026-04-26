from django.shortcuts import render
from .models import Product

# Create your views here.
def home(request):
    prods = Product.objects.all()
    return render(request,"home.html", {"prods": prods})