from django.shortcuts import redirect, render
from shop.models import Product, ProductImage,ProductVariant
from django.contrib import messages
from category.models import Category
from category.models import *
from offers.models import Offer
from django.contrib.auth.decorators import login_required
from authentication import *
from authentication.views import *
import base64
from django.shortcuts import get_object_or_404

# Create your views here.

def products(request):
    products = Product.objects.all()
    context = {
        'products' : products,
        
    }
    return render(request, 'adminpanel/page-products-grid-2.html', context)

def add_product(request):

    if request.method == 'POST':
        image = ''
        try:
            image = request.FILES['image']
        except:
            if image == '':
                messages.info(request,"Image field can't be empty")
                return redirect(add_product)
        
        name = request.POST['name']
        brand = request.POST['brand']
        category = request.POST['category']
        description = request.POST['desc']
        offer = request.POST['offer']
        
        try:
            Product.objects.get(product_name = name)
        except:
                check = [name,description]
                for values in check:
                    if values == '':
                        messages.info(request,'some fields are empty')
                        return redirect(add_product)
                    else:
                        pass    
                brand_instance = Brand.objects.get(id=brand)
                category_instance = Category.objects.get(id=category)
                offer_instance = None
                if offer:
                    offer_instance = Offer.objects.get(id=offer)

                Product.objects.create(
                    product_name=name,
                    brand=brand_instance,
                    category=category_instance,
                    description=description,
                    images=image,
                    offer=offer_instance,
                    
                ).save()
                product = Product.objects.get(product_name = name)
                # for image in images: 
                #     ProductImage.objects.create(product=product, pr_images=image)              
                
                messages.info(request,f'Product {name} created succefully')
                return redirect(add_product)
        else:
            messages.error(request,f'Product "{name}" already exist')
            return redirect(add_product)


    brands = Brand.objects.all()
    categories = Category.objects.all()
    offers = Offer.objects.all()

    context = {
        'categories' : categories,
        'brands' : brands,
        'offers' : offers,
    }
    return render(request, 'adminpanel/page-form-product-1.html', context)

def edit_product(request, id):

    if request.method == "POST":

        image = ''
        try:
            image = request.FILES['image']
            print(image)
            product = Product.objects.filter(id=id).first()
            product.images = image
            product.save()

        except:
            print('Hi')

        name = request.POST['name']
       
        brand = request.POST['brand']
        category = request.POST['category']
        price = request.POST['price']
        quantity = request.POST['quantity']
        offer = request.POST['offer']

        if name == '':
            messages.error(request,"Product name can't be null")
            return redirect(edit_product)
        
        if not price or not quantity:
            messages.error(request, "Price and quantity are required")
            return redirect(edit_product)
        
        offer_instance = None
        if offer:
            offer_instance = Offer.objects.get(id=offer)

        
        brand_instance = Brand.objects.get(id=brand)
        category_instance = Category.objects.get(id=category)

        product = Product.objects.filter(id=id).update(

            product_name=name,
            brand=brand_instance,
            category=category_instance,
            price = price,
            quantity = quantity,
            offer=offer_instance,
            
        )


        messages.success(request,f'{name} updated successfully')
        return redirect(products)
    
    
    offers = Offer.objects.all()
    product = Product.objects.get(id=id)
    brands = Brand.objects.all()
    categories = Category.objects.all()

 
    
    context = {

        "product": product,
        'categories' : categories,
        'brands' : brands,
        'offers' : offers,
      
    }

    return render(request, "adminpanel/product-update.html", context)


def delete_product(request, id):

    product = Product.objects.get(id=id)
    name = product.product_name
    product.delete()    
    messages.success(request,f'Product "{name}" deleted')
    return redirect(products)

# Category section

def add_category(request):
    
    if request.method == 'POST':        
        image = ''
        try:
            image = request.FILES['image']
        except:
            if image == '':
                messages.info(request,"Image field can't be empty")
                return redirect(add_category)
            
        name = request.POST['name']
        description = request.POST['desc']
        offer = ''
        try:
            offer = request.POST['offer']
        except Exception as e:
            print(e)
        check = [name]
        is_available = request.POST.get('is_available', False)        
        if is_available:
            is_available = True
        else:
            is_available = False 
        for values in check:
            if values == '':
                messages.info(request,'some fields are empty')
                return redirect(add_category)
            else:
                pass
            
        offer_instance = None
        if offer:
            offer_instance = Offer.objects.get(id=offer)
        try:
            Category.objects.get(category_name = name)
        except:
            Category.objects.create(category_name=name,cat_image=image,category_decs=description,).save()
            messages.success(request,f'Category "{name}" succesfully added')
        else:
            messages.error(request,f'Category "{name}" already exist')
            return redirect(add_category)
    if not request.user.is_authenticated and not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    offers = Offer.objects.all()
    categories = Category.objects.all()
    context = {

        'categories': categories,
        'offers': offers,
    }

    return render(request, 'adminpanel/page-categories.html', context)

def edit_category(request, id):
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['desc']
        offer = request.POST['offer']

        offer_instance = None
        if offer:
            offer_instance = Offer.objects.get(id=offer)

        category = Category.objects.filter(id=id).update(
            category_name=name,
            category_decs=description,
            offer=offer_instance,
        )
        messages.success(request,f'{name} updated successfully')
        return redirect(add_category)

    category = Category.objects.get(id=id)
    offers = Offer.objects.all()
    context = {
        'category' : category,
        'offers':offers,
    }
    return render(request, "adminpanel/update-category.html", context)


def delete_category(request, id):
    category = Category.objects.get(id=id)
    name = category.category_name
    category.is_available = False
    category.save()
    messages.success(request,f'Category "{name}" deleted')
    return redirect(add_category)

# brant section

def add_brand(request):
    if request.method == "POST":
        image = ''
        try:
            image = request.FILES['image']
        except:
            if image == '':
                messages.info(request,"Image field can't be empty")
                return redirect(add_brand)
        name = request.POST['name']
        desc = request.POST['desc']

        brand = Brand.objects.create(
            brand_name = name,
            brand_desc = desc,
            images = image,
        )
        brand.save()
        messages.success(request,f'Brand "{name}" created')
        return redirect(add_brand)
    brand = Brand.objects.all()
    context = {
        'brands' : brand,
    }
    return render(request,"adminpanel/brand.html", context)


def edit_brand(request, id):
    brand = Brand.objects.get(id=id)
    if request.method == "POST":
        image = ''
        try:
            image = request.FILES['image']
        except:
            if image == '':
                messages.info(request,"Image field can't be empty")
                return redirect(add_brand)
        name = request.POST['name']
        desc = request.POST['desc']
        Brand.objects.filter(id=id).update(
            brand_name = name,
            brand_desc = desc,
        )
        messages.success(request,f'{name} updated successfully')
        return redirect(add_brand)
    return render(request, 'adminpanel/editbrand.html', {'brand':brand,})

def delete_brand(request,id):
    brand = Brand.objects.get(id=id)
    name = brand.brand_name
    brand.is_available = False
    brand.save()
    messages.success(request,f'brand "{name}" deleted')
    return redirect(add_brand)


# View to display product variants for a given product
@login_required(login_url='handle_login')
def variant(request,id):
    if not request.user.is_superuser:
        return redirect(handlelogin)
    
     # Retrieve product variants associated with the given product ID
    variant = ProductVariant.objects.filter(product_id =id)
    context={
        'variant':variant
    }
    return render(request,'adminpanel/variant.html',context)

# View to add a new product variant
@login_required(login_url='handle_login')
def addvariant(request):
    if not request.user.is_superuser:
        return redirect(handlelogin)   
    pr = Product.objects.all()
    
    if request.method == 'POST':
        quantity = request.POST['quantity']
        price = request.POST['price']
        color = request.POST['color'] 
        product_id = request.POST['product']
        images = request.FILES.getlist('images')
        print(images,'fgh')
        product=Product.objects.get(id=product_id)   
        variant = ProductVariant(
            quantity = quantity,
            price = price,
            color=color, 
            product=product,
        )
        variant.save()

        # Add images to the newly created variant
        for image in images:
            ProductImage.objects.create(variant=variant, pr_images=image)  

        messages.success(request, 'variant added')
    return render(request, 'adminpanel/addvariant.html', {'products' : pr, })



# View to edit an existing product variant
@login_required(login_url='handle_login')
def editvariant(request, variant_id):
    if not request.user.is_superuser:
        return redirect('handle_login')

    try:
        variant = ProductVariant.objects.get(id=variant_id)
    except ProductVariant.DoesNotExist:
        # Handle the case where the variant doesn't exist
        return HttpResponse("Variant not found", status=404)

    pr = Product.objects.all()

    if request.method == 'POST':
        quantity = request.POST['quantity']
        price = request.POST['price']
        color = request.POST['color']
        product_id = request.POST['product']
        images = request.FILES.getlist('images')

        variant.quantity = quantity
        variant.price = price
        variant.color = color
        variant.product = Product.objects.get(id=product_id)
        variant.save()

        # Clear existing images and add new ones
        variant.images.clear()
        for image in images:
            ProductImage.objects.create(variant=variant, pr_images=image)

        messages.success(request, 'Variant updated')

    return render(request, 'adminpanel/editvariant.html', {'variant': variant, 'products': pr})
