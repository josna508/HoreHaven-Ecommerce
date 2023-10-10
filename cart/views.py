from django.shortcuts import render,redirect,get_object_or_404
from shop.models import Product,ProductVariant
from . models import Cart,CartItem
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from offers.models import Coupon

# Create your views here.
def _session_id(request):
    cart = request.session.session_key

    # if user is not loggined
    if not cart:
        cart = request.session.create()
    return cart


# for adding products to the cart
def add_cart(request, variant_id):
    variant = ProductVariant.objects.get(id = variant_id)
    product = variant.product
    try:
        # it will retreive existing cart
        cart = Cart.objects.get(session_id=_session_id(request))
    except Cart.DoesNotExist:
        # if there is no cart  it will create a new cart
        cart = Cart.objects.create(
            session_id = _session_id(request)
        )
   
    cart.coupon = None
    cart.save()

    try:
        # if the product already in the cart it will increase cart item quantity
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if ((variant.quantity)-(cart_item.quantity + 1)) < 0:
            response_data = {
                'error': 'Out of stock',
            }
            return JsonResponse(response_data, status=400)

        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        # If the product is not in the cart, create a new cart item
        if request.user.is_authenticated:
            if ((variant.quantity)- 1) < 0:
                response_data = {
                    'error': 'Out of stock',
                }
                return JsonResponse(response_data, status=400)
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1, 
                cart = cart,
                user = request.user,
                variant = variant
            )
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1, 
                cart = cart,
            )
            cart_item.save()
    return JsonResponse(response_data)




# For showing cart items on cart page 
def cart(request, total=0, quantity=0, cart_items=None,count=0,coupons=None, cart=None, subtotal=0, discount_amount=0):
    offer_price = 0
    try:
        print(request.session)
        cart,_ = Cart.objects.get_or_create(session_id = _session_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
            
        for cart_item in cart_items:
            total += cart_item.sub_total()
            quantity += cart_item.quantity
            count += 1
            subtotal = total

            if cart_item.product.offer:
                offer_price +=(cart_item.variant.price*cart_item.product.offer.off_percent/100)

            elif cart_item.product.category.offer:
                offer_price +=(cart_item.variant.price*cart_item.product.category.offer.off_percent/100)

        
       
    except:
        pass

      # for adding coupons
    if request.method == "POST":
        coup = request.POST['search']
        try:
            coupon = Coupon.objects.get(coupon_code = coup)

            # Check if the coupon is expired
            if coupon.is_expired():
                messages.error(request, 'Coupon is expired')
                return redirect('cart')
            
            # Check if the total amount is less than the minimum required for the coupon
            if coupon.min_amount > total:
                messages.error(request, f'Amount should be greater than {coupon.min_amount}')
                return redirect('cart')
            
            cart = Cart.objects.get(session_id = _session_id(request))

            discount_amount = total * coupon.off_percent / 100

            if discount_amount > coupon.max_discount:
                discount_amount = coupon.max_discount

            subtotal = total
            total -= discount_amount
           

            cart.coupon = coupon
            cart.save()
                
        except Coupon.DoesNotExist:
            messages.error(request, 'Coupon not found')
            return redirect('cart')
        
        
    if cart.coupon:
        discount_amount = total * cart.coupon.off_percent / 100

        if discount_amount > cart.coupon.max_discount:
            discount_amount = cart.coupon.max_discount
    total -= offer_price
    coupons = Coupon.objects.all()
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'count': count,
        'coupons': coupons,
        'cart':cart,
        'discount_amount':discount_amount,
        'sub_total':subtotal,
        'offer_price':offer_price,
    }


    return render(request, "cart.html", context)

# Function to remove a product from the cart or reduce its quantity
def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(session_id=_session_id(request))
    cart.coupon = None
    cart.save()
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user)
    else:
        
        cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')






# Function to delete a product from the cart
def delete_cart(request, cartItem_id):
    print(cartItem_id)

    cartItem = CartItem.objects.get(id=cartItem_id)
    cartItem.delete()

    return redirect('cart')
                       

def update_cart(request, product_id):
    print('dfdfdfdf')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            # Increase the quantity of the product in the cart
            cart_item = CartItem.objects.get(product_id=product_id)
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            # Decrease the quantity of the product in the cart
            cart_item = CartItem.objects.get(product_id=product_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # Optionally, you can remove the item from the cart if the quantity reaches zero
                cart_item.delete()

    # Redirect back to the cart page or wherever you want
    return redirect('cart')  # 'cart' should match your cart page URL name
