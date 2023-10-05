from django.contrib import admin
from .models import *

# Register your models here.

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)






