from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from .models import Cart, CartItem, user_data
from home.models import products


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, "register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "register.html")

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        credential = request.POST.get("credential", "").strip()
        password = request.POST.get("password", "")

        if not credential or not password:
            messages.error(request, "Please enter your email or phone number, and password.")
            return render(request, "login.html")

        user_obj = User.objects.filter(email=credential).first()

        if not user_obj:
            try:
                ud = user_data.objects.get(phone=credential)
                user_obj = User.objects.filter(username=ud.user_name).first()
            except (user_data.DoesNotExist, ValueError):
                user_obj = None

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
        else:
            user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid credential or password.")
            return render(request, "login.html")

    return render(request, "login.html")


@login_required
def profile_view(request):
    try:
        user_info = user_data.objects.get(user_name=request.user.username)
    except user_data.DoesNotExist:
        user_info = None

    return render(request, "profile.html", {"user_info": user_info})


def logout_view(request):
    if request.method == "POST":
        auth_logout(request)
        return redirect("home")

    return render(request, "logout.html")


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.total_price for item in items)

    return render(request, "cart.html", {
        "items": items,
        "total": total
    })


@login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(products, id=product_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item = CartItem.objects.filter(cart=cart, product_id=product.id).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            CartItem.objects.create(
                cart=cart,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                product_image=product.image,
                quantity=1
            )

        messages.success(request, f"{product.name} added to cart.")
        return redirect("cart_view")
    return redirect("home")


@login_required
def change_password_view(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, "change_password.html")

        if not request.user.check_password(old_password):
            messages.error(request, "Incorrect old password.")
            return render(request, "change_password.html")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, "change_password.html")

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully.")
        return redirect("profile")

    return render(request, "change_password.html")