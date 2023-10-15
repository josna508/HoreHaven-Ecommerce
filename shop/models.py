from django.db import models
from django.urls import reverse
from category.models import Category, Brand
from offers.models import Offer

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=100, unique = True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, default=None)
    description = models.TextField(max_length=500, blank=True)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    images = models.ImageField(upload_to="photos/categories",blank=True,null=True)

   

    # def is_outofstock(self):
    #     return self.stock <= 0 

   
    def __str__(self):
        return self.product_name
    
    def get_offer_price(self,variant):
        if self.offer:
            return int(variant.price - (variant.price * self.offer.off_percent / 100))
        else:
            return self.price  # No offer, so return the regular price

    def get_offer_price_by_category(self,variant):
        if self.category and self.category.offer:
            return int(variant.price - (variant.price * self.category.offer.off_percent / 100))
        else:
            return self.price  # No offer for the category, so return the regular price
        
    def get_variant(self, color):
        return self.productVariant.get(color=color)



class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="productVariant"
    )
    quantity = models.IntegerField(default=0)
    price = models.IntegerField()
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.color



class ProductImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="product_images",blank=True,null=True)
    pr_images = models.ImageField(upload_to="photos/product")


