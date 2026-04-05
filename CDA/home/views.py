from django.shortcuts import render
from .models import products

# Create your views here.
def home(request):
    prods = products.objects.all()
    return render(request,"home.html", {"prods": prods})