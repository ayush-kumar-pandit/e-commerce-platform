from django.db import models

# Create your models here.
class products(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    desc = models.TextField()
    image = models.ImageField(upload_to = 'images')