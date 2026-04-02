from django.db import models

# Create your models here.
class User_Data(models.Model):
    user_name = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    phone = models.IntegerField()
    mail = models.EmailField(max_length=254)
    address = models.TextField()