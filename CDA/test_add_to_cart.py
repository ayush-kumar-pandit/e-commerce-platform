import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CDA.settings")
django.setup()

from django.contrib.auth.models import User
from home.models import products
from user.models import Cart, CartItem

user, _ = User.objects.get_or_create(username='testuser')
product, _ = products.objects.get_or_create(name='Test Product', price=100)

cart, _ = Cart.objects.get_or_create(user=user)

print("Adding to cart...")
cart_item = CartItem.objects.create(
    cart=cart,
    product_id=product.id,
    product_name=product.name,
    product_price=product.price,
    product_image=product.image,
    quantity=1
)
print("Added successfully!")
