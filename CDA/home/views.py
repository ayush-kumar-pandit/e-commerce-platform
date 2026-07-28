from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Product, ProductImage, OurScience
from .forms import ReviewForm


def product_detail_view(request, id):
    """
    Display product details with image gallery.
    Shows all product images in order of display_order.
    """
    product = get_object_or_404(Product, id=id)
    # Get all images for this product, ordered by display_order
    images = product.images.all().order_by('display_order')
    
    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        if 'rating' in request.POST: # Check if it's the review form
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been added successfully!')
                return redirect('product_detail', id=product.id)
    else:
        form = ReviewForm()
        
    reviews = product.reviews.all()
    
    context = {
        'product': product,
        'images': images,
        'form': form,
        'reviews': reviews,
    }
    return render(request, "product_detail.html", context)


def home(request):
    """Display all products on home page"""
    prods = Product.objects.all()
    return render(request, "home.html", {"prods": prods})


def shop_view(request):
    """
    Shop view with search, filtering, and sorting functionality.
    """
    prods = Product.objects.all()

    # Search
    q = request.GET.get('q')
    if q:
        prods = prods.filter(Q(name__icontains=q) | Q(desc__icontains=q))

    # Filter by price
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

    # Sort products
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
        # Default sorting by id to keep order consistent
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
    """Display about page"""
    return render(request, "about.html")


def contact_view(request):
    """Display contact page"""
    return render(request, "contact.html")


def our_science_view(request):
    """
    Display 'Our Science' section with content.
    Fetches the first OurScience object from database.
    """
    science_data = OurScience.objects.first()
    return render(request, "our_science.html", {"science_data": science_data})
