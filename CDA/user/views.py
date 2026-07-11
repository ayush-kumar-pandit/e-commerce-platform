from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import PasswordChangeForm
from .models import Cart, CartItem, UserProfile
from home.models import Product
from .forms import UserRegistrationForm, UserLoginForm
import random
from django.core.mail import send_mail
from django.conf import settings


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Do NOT save the user yet — store registration data in session
            pending_data = {
                'full_name': form.cleaned_data['full_name'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }

            # Generate OTP
            otp = str(random.randint(100000, 999999))

            # Store pending data and OTP in session
            request.session['pending_registration'] = pending_data
            request.session['registration_otp'] = otp

            # Send Email
            subject = 'Verify your email for Bharat Sanjeevani Ayurveda'
            message = (
                f'Hello {pending_data["full_name"]},\n\n'
                f'Your OTP for registration is: {otp}\n\n'
                f'This OTP is valid for this session only. Do not share it with anyone.\n\n'
                f'– Bharat Sanjeevani Ayurveda Team'
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [pending_data['email']]

            try:
                send_mail(subject, message, email_from, recipient_list)
                messages.success(request, "OTP sent to your email. Please verify.")
            except Exception as e:
                print(f"Error sending email: {e}")
                messages.error(request, "Failed to send OTP email. Please try again.")
                return render(request, "register.html", {"form": form})

            return redirect("verify_otp")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})

def verify_otp_view(request):
    pending_data = request.session.get('pending_registration')
    stored_otp = request.session.get('registration_otp')

    if not pending_data or not stored_otp:
        messages.error(request, "No registration in progress. Please register again.")
        return redirect("register")

    if request.method == "POST":
        otp_entered = request.POST.get('otp', '').strip()

        if otp_entered == stored_otp:
            # OTP is correct — now create the user
            import uuid
            email = pending_data['email']
            base_username = email.split('@')[0] if '@' in email else 'user'
            username = f"{base_username}_{uuid.uuid4().hex[:6]}"

            user = User(
                username=username,
                email=email,
                first_name=pending_data['full_name'],
                is_active=True,
            )
            user.set_password(pending_data['password'])
            user.save()

            # Clear session data
            del request.session['pending_registration']
            del request.session['registration_otp']

            messages.success(request, "Email verified successfully! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "verify_otp.html", {"user_email": pending_data.get('email', '')})


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