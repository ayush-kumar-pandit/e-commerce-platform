from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    desc = models.TextField()
    image = models.ImageField(upload_to = 'images')

    def __str__(self):
        return self.name