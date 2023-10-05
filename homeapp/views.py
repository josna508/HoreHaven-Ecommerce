from django.shortcuts import render
from django.urls import path
from category.models import Brand
from category.models import Category
from shop.models import Product
# Create your views here.

def index(request):
    brand = Brand.objects.filter(is_available = True)
    category = Category.objects.filter(is_available= True)
    product = Product.objects.filter(is_available = True)
    context = {
        'brand':brand,
        'categorys':category,
        'products':product,

        }
    return render(request,'index.html',context)


