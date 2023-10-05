from django.shortcuts import render,get_object_or_404
from category.models import Brand
from category.models import Category
from .models import Product
from django.db.models import Q
from django.utils import encoding
from django.db.models import Min, Max
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

def shop(request):
    # Retrieve available brands, categories, and products
    brand = Brand.objects.filter(is_available = True)
    category = Category.objects.filter(is_available= True)
    product = Product.objects.filter(is_available = True)
    context = {
        'brand':brand,
        'categorys':category,
        'products':product,

        }
    
    return render(request,"shop.html",context)

def product_details(request, id):
      # Retrieve available brands, categories, and a specific product
    brand = Brand.objects.filter(is_available = True)
    category = Category.objects.filter(is_available= True)
    single_product = Product.objects.get(id = id)

  

    # Check if a color parameter is provided in the GET request
    if request.GET.get("color"):
        color = request.GET.get("color")
        print(color)
        variant = single_product.get_variant(color)
        context = {
           'single_product' : single_product,
            'brand':brand,
            'categorys':category,
            "selected_color": color,
            "selected_variant": variant,

            }
            
    else:
        
        # If no color parameter, use the first available variant
        variant = single_product.productVariant.first()
        context = {
            'single_product' : single_product,
            'brand':brand,
            'categorys':category,
            "selected_color": variant.color,
            "selected_variant": variant,
            "images":variant.product_images.all()

            }
        
    if single_product.offer:
        offer_price = variant.price-(variant.price*single_product.offer.off_percent/100)
    elif single_product.category.offer:
        offer_price = variant.price-(variant.price*single_product.category.offer.off_percent/100)
    else:
        offer_price = 0

    context['offer_price']= offer_price

    return render(request,"product_details.html",context)


# def search_result(request):
#     search = request.GET["searched"]
#     products = Product.objects.filter(product_name__icontains=search)
#     prod = products.filter(is_available = True)
#     context = {"products": prod, "search": search}
#     return render(request, "shop.html", context)


def search_result(request):
    search_term = request.GET.get("searched")
    print("Received search term:", search_term)
    
    if search_term:
        # Perform a case-insensitive search on product names and descriptions
        encoded_search_term = encoding.force_str(search_term)
        print("Encoded search term:", encoded_search_term)
        
        q_objects = Q(product_name__icontains=encoded_search_term) | Q(product_name__icontains=search_term)
        print("Generated Q objects:", q_objects)
        
        products = Product.objects.filter(q_objects, is_available=True)
        print("Filtered products:", products)
        
        context = {"products": products, "search": search_term}
    else:
         # If no search term provided, return an empty result
        context = {"products": [], "search": ""}
    
    return render(request, "shop.html", context)



def filtered_products(request):
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_option = request.GET.get('sort')  # Get the selected sorting option from the query parameters

    # Query the database to get the filtered products
    filtered_products = Product.objects.filter(is_available=True)
    c = 0



  # Apply filters based on user selections
    if search_query:
        filtered_products = filtered_products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        c = filtered_products.count()

    if selected_categories:
        filtered_categories = Category.objects.filter(category_name__in=selected_categories)
        filtered_products = filtered_products.filter(category__in=filtered_categories)
        c = filtered_products.count()

    if selected_brands:
        filtered_brands = Brand.objects.filter(brand_name__in=selected_brands)
        filtered_products = filtered_products.filter(brand__in=filtered_brands)
        c = filtered_products.count()

    if min_price and max_price:
        filtered_products = filtered_products.filter(price__gte=min_price, price__lte=max_price)
        c = filtered_products.count()
    
     # Apply sorting logic based on the selected sort option
    if sort_option == 'price_high_to_low':
        # Sort by the highest price among variants
        filtered_products = filtered_products.annotate(
            highest_price=Max('productVariant__price')
        ).order_by('-highest_price')
    elif sort_option == 'low_to_high':
        # Sort by the lowest price among variants
        filtered_products = filtered_products.annotate(
            lowest_price=Min('productVariant__price')
        ).order_by('lowest_price')
    elif sort_option == 'latest':
        # Sort by the created date of the product
        filtered_products = filtered_products.order_by('-created_date')  # Assuming 'created_date' is the field for product creation date
    categories = Category.objects.all()
    brand = Brand.objects.all()

    context = {
        'products': filtered_products,
        'categorys': categories,
        'brand': brand,
        'c': c,
        'f': True,
    }

    return render(request, 'shop.html', context)




