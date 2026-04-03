from django.db import models

# Create your models here.
class user_data(models.Model):
    user_name = models.CharField(max_length = 20)
    name = models.CharField(max_length = 50)
    password = models.CharField()
    phone = models.BigIntegerField()
    email = models.EmailField(max_length=254)
    address = models.TextField()