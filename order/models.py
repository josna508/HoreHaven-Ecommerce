from django.db import models
from django.contrib.auth.models import User
from user_profile.models import UserAddress
from shop.models import Product, ProductVariant
import string
import random
from datetime import datetime
from django.utils import timezone

# Create your models here.
def generate_order_id():
    """Generate a 14-character order ID"""
    while True:
        letters = string.ascii_uppercase + string.digits
        order_id = ''.join(random.choice(letters) for i in range(9))
        year = str(datetime.now().year)[-2:]
        month = str(datetime.now().month)[-2:]
        day = str(datetime.now().day)
        hour = str(datetime.now().hour)
        new_id = 'HH' + year + month + day + hour+ order_id
        return new_id
    
class PaymentMethod(models.Model):
    method = models.CharField(max_length=225)


class Payment(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('done', 'Done'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount_paid = models.FloatField(null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.payment_method.method
    

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,null=True, blank=True)
    order_id = models.CharField(max_length=50, default=generate_order_id, unique=True)
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL,null=True, blank=True)
    order_total = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    coupon = models.ForeignKey('offers.Coupon', on_delete=models.SET_NULL,null=True, blank=True)
    coupon_discount = models.BigIntegerField(null=True,blank=True)

    def __str__(self) -> str:
        return self.order_id
    

class OrderItem(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('returned', 'Returned'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,null=True, blank=True)
    product_price = models.FloatField()
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, blank=True, null=True)


    def sub_total(self):
        return self.product_price * self.quantity
    
    def get_full_name(self):
        print(self.order.address)
        return f'{self.order.address.fname} {self.order.address.lname}'
    
    def __str__(self) -> str:
        return self.product.product_name


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    type = models.CharField(max_length=100,null=True,blank=True)
    description = models.CharField(max_length=100,null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True,null=True,blank=True)