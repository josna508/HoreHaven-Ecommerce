from django.db import models
import random
from django.contrib.auth.models import User 
from shop.models import Product
from offers.models import Coupon
from shop.models import ProductVariant

# Create your models here.
def generate_cart_id():
    """Generate a unique eight-digit cart ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not Cart.objects.filter(cart_id=new_id).exists():
            return new_id

class Cart(models.Model):
    cart_id = models.IntegerField(unique=True,default=generate_cart_id)
    session_id = models.TextField(default=None)
    date_created = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Add a method to calculate the quantity
    def calculate_quantity(self):
        # Calculate the total quantity based on cart items
        quantity = sum(item.quantity for item in self.cartitem_set.all())
        return quantity
    
    def calculate_total(self):
        # Calculate the total based on cart items
        total = sum(item.sub_total() for item in self.cartitem_set.all())
        return total
    
    def __str__(self):
        return str(self.cart_id)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart =  models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)

    def sub_total(self):
        return self.variant.price * self.quantity
    
    def sub_total_with_offer(self):
        return int((self.sub_total()) - ( self.sub_total() * self.product.offer.off_percent / 100))
    
    def sub_total_with_offer_category(self):
        return int((self.sub_total()) - ( self.sub_total() * self.product.category.offer.off_percent / 100))

    def __str__(self):
        return self.product.product_name