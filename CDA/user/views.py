from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from .models import Cart, CartItem, UserProfile, OTPVerification
from home.models import Product
from .forms import UserRegistrationForm, UserLoginForm
import random
from django.core.mail import send_mail
from django.conf import settings


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False # Deactivate account till it is verified
            user.save()

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            OTPVerification.objects.create(user=user, otp=otp)

            # Send Email
            subject = 'Verify your email for Bharat Sanjeevani Ayurveda'
            message = f'Your OTP for registration is {otp}.'
            email_from = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@bharatsanjeevani.com'
            recipient_list = [user.email]
            
            try:
                send_mail(subject, message, email_from, recipient_list)
            except Exception as e:
                print(f"Error sending email: {e}")

            request.session['registration_user_id'] = user.id
            messages.success(request, "OTP sent to your email. Please verify.")
            return redirect("verify_otp")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})

def verify_otp_view(request):
    user_id = request.session.get('registration_user_id')
    if not user_id:
        messages.error(request, "No registration in progress. Please register again.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        otp_entered = request.POST.get('otp', '').strip()
        otp_record = getattr(user, 'otp_verification', None)

        if otp_record and otp_record.otp == otp_entered:
            user.is_active = True
            user.save()
            otp_record.delete()
            del request.session['registration_user_id']
            
            messages.success(request, "Email verified successfully! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "verify_otp.html", {"user_email": user.email})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data['credential']
            password = form.cleaned_data['password']

            user = authenticate(request, username=credential, password=password)

            if user is not None:
                login(request, user)
                display_name = user.get_full_name() or user.username
                messages.success(request, f"Welcome back, {display_name}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid credential or password.")
    else:
        form = UserLoginForm()

    return render(request, "login.html", {"form": form})


@login_required
def profile_view(request):
    user_info, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if 'address' in request.POST:
            new_address = request.POST.get("address", "").strip()
            if new_address:
                user_info.address = new_address
                user_info.save()
                messages.success(request, "Address updated successfully.")
            else:
                messages.error(request, "Address cannot be empty.")
        
        if 'image' in request.FILES:
            user_info.image = request.FILES['image']
            user_info.save()
            messages.success(request, "Profile image updated successfully.")

        return redirect("profile")

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
        product = get_object_or_404(Product, id=product_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item = CartItem.objects.filter(cart=cart, product=product).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=1
            )

        messages.success(request, f"{product.name} added to cart.")
        return redirect("cart_view")
    return redirect("home")


@login_required
def update_cart_item(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if action == 'increase':
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    return redirect('cart_view')


@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = item.product.name
    item.delete()
    messages.success(request, f"{product_name} removed from cart.")
    return redirect('cart_view')


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect("profile")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)

    for field in form.fields.values():
        field.widget.attrs.update({'class': 'w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:border-green-700 focus:ring-1 focus:ring-green-700 transition'})

    return render(request, "change_password.html", {"form": form})