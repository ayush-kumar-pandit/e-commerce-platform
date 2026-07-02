from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    desc = models.TextField()
    image = models.ImageField(upload_to = 'images')


    def __str__(self):
        return self.name

class OurScience(models.Model):
    title = models.CharField(max_length=100, default="Our Science")
    heading = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='science_images', blank=True, null=True)

    def __str__(self):
        return self.title