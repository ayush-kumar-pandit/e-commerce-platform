from django.db import models
from django.contrib.auth.models import User


class user_data(models.Model):
    user_name = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    phone = models.BigIntegerField()
    email = models.EmailField(max_length=254)
    address = models.TextField()
    gender = models.TextField()
    age = models.IntegerField()

    def __str__(self):
        return self.user_name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to='cart_products/', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product_price * self.quantity