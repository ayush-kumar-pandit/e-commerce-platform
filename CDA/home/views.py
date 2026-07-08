from django.shortcuts import render
from django.db.models import Q
from .models import Product, OurScience

# Create your views here.
def home(request):
    prods = Product.objects.all()
    return render(request,"home.html", {"prods": prods})

def shop_view(request):
    prods = Product.objects.all()

    # Search
    q = request.GET.get('q')
    if q:
        prods = prods.filter(Q(name__icontains=q) | Q(desc__icontains=q))

    # Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        try:
            prods = prods.filter(price__gte=int(min_price))
        except ValueError:
            pass
            
    if max_price:
        try:
            prods = prods.filter(price__lte=int(max_price))
        except ValueError:
            pass

    # Sort
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        prods = prods.order_by('price')
    elif sort == 'price_desc':
        prods = prods.order_by('-price')
    elif sort == 'name_asc':
        prods = prods.order_by('name')
    elif sort == 'name_desc':
        prods = prods.order_by('-name')
    else:
        # Default sorting by pk or id to keep order consistent
        prods = prods.order_by('id')

    context = {
        'prods': prods,
        'q': q or '',
        'min_price': min_price or '',
        'max_price': max_price or '',
        'sort': sort or '',
    }
    return render(request, "shop.html", context)

def about_view(request):
    return render(request, "about.html")

def contact_view(request):
    return render(request, "contact.html")

def our_science_view(request):
    # Fetch the first OurScience object, or None if it doesn't exist yet
    science_data = OurScience.objects.first()
    return render(request, "our_science.html", {"science_data": science_data})