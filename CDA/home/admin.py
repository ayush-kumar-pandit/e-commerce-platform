from django.contrib import admin
from .models import Product, ProductImage, OurScience


class ProductImageInline(admin.TabularInline):
    """
    Inline admin for managing multiple product images.
    Allows adding/editing images directly within Product admin page.
    """
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'display_order', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    ordering = ['display_order']


class ProductAdmin(admin.ModelAdmin):
    """
    Enhanced Product admin with image gallery management.
    """
    list_display = ('name', 'price', 'image_count', 'created_at')
    list_filter = ('created_at', 'price')
    search_fields = ('name', 'desc')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'desc')
        }),
        ('Primary Image', {
            'fields': ('image',),
            'description': 'This image is displayed in product listings'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_count(self, obj):
        """Display number of images for this product"""
        count = obj.images.count()
        return f"{count} image{'s' if count != 1 else ''}"
    image_count.short_description = 'Gallery Images'


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(OurScience)
