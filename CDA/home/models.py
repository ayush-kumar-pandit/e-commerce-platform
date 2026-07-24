from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    desc = models.TextField()
    image = models.ImageField(upload_to='products/main_images', help_text='Primary product image (displayed in list)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """
    Store multiple images for a single product.
    Similar to Flipkart/Amazon product galleries.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True, help_text='Alternative text for accessibility')
    is_primary = models.BooleanField(default=False, help_text='Set as primary product image')
    display_order = models.PositiveIntegerField(default=0, help_text='Order of images in gallery (0 = first)')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'uploaded_at']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return f"{self.product.name} - Image {self.display_order + 1}"

    def save(self, *args, **kwargs):
        """Ensure only one primary image per product"""
        if self.is_primary:
            # Remove primary status from other images of same product
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class OurScience(models.Model):
    title = models.CharField(max_length=100, default="Our Science")
    heading = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='science_images', blank=True, null=True)

    def __str__(self):
        return self.title
