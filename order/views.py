from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from cart.models import *
from .models import *
from django.views.decorators.csrf import csrf_exempt
from cart.views import _session_id
from django.contrib.auth.decorators import login_required
import razorpay
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from .models import Wallet
from decimal import Decimal
# from authentication.views import handle_login
# Create your views here.




# Payment confirmation view
@login_required(login_url='handlelogin')
def payments(request, total = 0, pretotal=0):

    # Check if the user is authenticated
    if request.user.is_authenticated:
    # Create a Payment instance for cash on delivery
        payment = Payment(
            user = request.user,
            payment_method ="cash on delivery",
        )
        payment.save()
    # Get the latest order for the user and update payment and status
        order = Order.objects.filter(user=request.user).order_by('-id').first()
        order.payment = payment
        order.status = 'accepted'
        order.save()

    # move cart items to ordered items and calculate the total
        cart_items = CartItem.objects.filter(user=request.user)
        for cart_item in cart_items:
            product_price = 0
            if cart_item.product.offer:
                product_price = cart_item.product.get_offer_price(cart_item.variant)
            elif cart_item.product.category.offer:
                product_price = cart_item.product.get_offer_price_by_category(cart_item.variant)
            else:
                product_price = cart_item.variant.price

            orderitem = OrderItem(
                user = request.user,
                order = order,
                product = cart_item.product,
                payment = payment,
                product_price = product_price,
                quantity = cart_item.quantity,
                status = 'accepted',
            )
            orderitem.save()

            total += orderitem.sub_total()


    
        # Reduce stock of ordered product
            product = Product.objects.get(id=cart_item.product.id)
            cart_item.variant.quantity -= cart_item.quantity
            product.save()
        

        # Send an order confirmation email to the user
        mess=f'Hello\t{request.user.username},\nYour Order of { order.order_id } has confirmed.\nThanks!'
        send_mail(
        "Thank you for the order",
        mess,
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False
        )

        # Removing Cart items
        CartItem.objects.filter(user=request.user).delete()
        cart = Cart.objects.get(session_id=_session_id(request))
        cart.coupon = None
        cart.save()

        orderitems = OrderItem.objects.filter(user=request.user, order=order)
        if order.coupon_discount:
            pretotal=total

        context = {
            'order' : order,
            'orderitems' : orderitems,
            'total' : total,
            'pretotal':pretotal,
            
        }
   

        return render(request, "confirm.html", context)

    # return render(request, 'payment.html')

# Place order view
@login_required(login_url='handlelogin')
def place_order(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        current_user = request.user
        total = 0
        discount_amount = None
        cart_items = CartItem.objects.filter(user=current_user)
        cart_count = cart_items.count()
        off_percent = None
        discount_amnt = 0
        coupon_discount = 0
        address = None 

         # Calculate the total order amount
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.variant.quantity:
                print("cart item out of stock")
                return redirect('cart')
            if cart_item.product.offer:
                total += cart_item.sub_total_with_offer()
            elif cart_item.product.category.offer:
                total += cart_item.sub_total_with_offer_category()
            else:
                total += cart_item.sub_total()
        cart = Cart.objects.get(session_id=_session_id(request))
        if cart.coupon:
            discount_amount = total * cart.coupon.off_percent / 100

            if discount_amount > cart.coupon.max_discount:
                discount_amount = cart.coupon.max_discount

            total -= discount_amount
        if cart_count <= 0:
            return redirect('shop')

        if request.method == "POST":
            # Get user input for address
            fname = request.POST.get('fname')
            lname = request.POST['lname']
            ph_no = request.POST['ph_no']
            house = request.POST['house']
            city = request.POST['city']
            state = request.POST['state']
            country = request.POST['country']
            user=request.user
            

             # Create a UserAddress object with the provided address information
            address = UserAddress.objects.create(
                    fname = fname,
                    lname = lname,
                    contact_number = ph_no,
                    house_name = house,
                    user=user,
                    city = city,
                    state = state,
                    country = country,
            )

        data = Order()
        data.user = current_user
        data.order_total = total
        data.address = address

        # Apply coupon discount if available
        if cart.coupon:
            discount_amount = total * cart.coupon.off_percent / 100
            if discount_amount > cart.coupon.max_discount:
                discount_amount = cart.coupon.max_discount
            total -= discount_amount
            data.coupon_discount = discount_amount
            data.coupon = cart.coupon
            data.order_total = total
        data.save()
        
        # Retrieve the created order for further processing
        order = Order.objects.get(user = current_user, status=data.status, order_id=data.order_id)
       
        # Create a Razorpay payment for the order 
        client = razorpay.Client(auth= ( settings.KEY, settings.KEY_SECRET ))
        payment = client.order.create({'amount' :total * 100 , 'currency' :'INR', 'payment_capture' : 1 })
        


        context = {
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'payment' : payment,
            'discount_amount': discount_amount,
        }
        return render(request,'payment.html', context)

# View to display user's orders
@login_required(login_url='handlelogin')    
def my_orders(request):
    # Retrieve orders for the authenticated user excluding pending orders
    myorders = OrderItem.objects.filter(Q(user=request.user) & ~Q(status='pending')).order_by('-id')
    context = {
        "myorders":myorders,
    }
    return render(request, 'myorders.html', context)
  
# View to cancel orders
@login_required(login_url='handlelogin')
def cancel_orders(request, id):
    print('pppppppppppppppppppppppppppp2')
    user = request.user
    print(user,'yyyyyyyyyyyyyyyyyyyyyyyy')
     
    item = OrderItem.objects.get(id = id)
    wallet, _ = Wallet.objects.get_or_create(user = user)
    
    # Check if the payment method for the order is 'cash on delivery'
    if item.order.payment.payment_method == 'cash on delivery':
            print('456378928272')
            
            # Check if the item has a variant before accessing its quantity
            if item.variant:
                quantity = item.quantity
                item.variant.quantity += quantity
                item.variant.save()

            

    else:
        print('qqqqqqqqqqqqqqqq', item.ORDER_STATUS)
        if item.variant:
            quantity = item.quantity
            item.variant.quantity += quantity
            item.variant.save()

        print('rrrrrrrrrrrrr',item.sub_total())
        print('Item Subtotal:', item.sub_total)

        # Replace with the actual method to calculate subtotal
        if wallet:
            wallet.amount += Decimal(str(item.sub_total()))
            wallet.save()
    
    item.status = 'cancelled'
    item.save()
            

       

     # Send an email notification to the user about the cancelled order
    current_user = request.user
    subject = "Cancell order succesfull!"
    mess = f'Greetings {current_user.first_name}.\nYour Order {item.order.order_id} has been cancelled. \nThank you for shopping with us!'
    send_mail(
            subject,
            mess,
            settings.EMAIL_HOST_USER,
            [current_user.email],
            fail_silently = False
    )
    return redirect(my_orders)


# after razorpay payment

# this method that redirecting from razorpay webiste. this method will redirect to success function
@csrf_exempt
def pre_success(request):
    return redirect(success)


# for order confirmation page and adding payment details
@login_required(login_url='handlelogin')
def success(request, total = 0):
        payment_method = 'razorpay'
         # Create a Payment instance and save it to the database
        payment = Payment(
            user = request.user,
            payment_method = payment_method,
            status = 'Paid'
        )
        payment.save()
         # Retrieve the latest order for the authenticated user and update payment and status
        order = Order.objects.filter(user=request.user).order_by('-id').first()
        order.payment = payment
        order.status = 'accepted'
        order.save()
        cart_items = CartItem.objects.filter(user=request.user)
           # Initialize the 'total' variable to calculate the total order amount
        for cart_item in cart_items:
            product_price = 0
             # Determine the product price based on offers or category offers
            if cart_item.product.offer:
                product_price = cart_item.product.get_offer_price(cart_item.variant)
            elif cart_item.product.category.offer:
                product_price = cart_item.product.get_offer_price_by_category()
            else:
                product_price = cart_item.variant.price
            orderitem = OrderItem(
                user = request.user,
                order = order,
                product = cart_item.product,
                payment = payment,
                product_price = product_price,
                quantity = cart_item.quantity,
                status = 'accepted',
            )
            orderitem.save()

            total += orderitem.sub_total()


    
        # Reduce stock of ordered product
            product = Product.objects.get(id=cart_item.product.id)
            cart_item.variant.quantity -= cart_item.quantity
            product.save()
        
        # order message
        mess=f'Hello\t{request.user.username},\nYour Order of { order.order_id } has confirmed.\nThanks!'
        send_mail(
        "Thank you for the order",
        mess,
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False
        )
        if order.coupon_discount:
            pretotal=total
            total -= order.coupon_discount
        else:
            pretotal = 0

        orderitems = OrderItem.objects.filter(user=request.user, order=order)
        # Removing Cart items
        CartItem.objects.filter(user=request.user).delete() 
        context = {
            'order' : order,
            'orderitems' : orderitems,
            'total' : total,
            'pretotal':pretotal,
            
        }
        return render(request, "confirm.html", context)


@login_required(login_url='handlelogin')
def return_order(request, id):
    item = OrderItem.objects.get(id=id)

    
    # Check if the payment method is not 'cash on delivery' and there is a coupon
    if item.order.payment.payment_method != 'cash on delivery' and item.order.coupon:
        item.status = 'returned'
        quantity = item.quantity
        item.product.stock += quantity
        item.save()

    else:
        item.status = 'returned'
        quantity = item.quantity

        item.product.stock += quantity
        item.save()
        
    
    # Send an email to the user
    current_user = request.user
    subject = "Returned Order Successful!"
    message = f'Greetings {current_user.first_name}.\nYour Order {item.order.order_id} has been returned. \nThank you for shopping with us!'
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [current_user.email],
        fail_silently=False
    )
    
    return redirect(my_orders)
