from django.shortcuts import render
from order.models import *
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='admin_login')
def order_details(request):
    if not request.user.is_authenticated and not request.user.is_superuser:
        return render(request, 'index.html')
    order_items = OrderItem.objects.all()
    
    context = {
        'order_items' : order_items,  # Include the order items in the context for rendering
    }
    return render(request, 'adminpanel/page-orders-1.html', context)

@login_required(login_url='admin_login')
def order_manage(request, id):
    if not request.user.is_authenticated and not request.user.is_superuser:
        return render(request, 'index.html')
    
      # Retrieve a specific order item by its ID
    cart_item = OrderItem.objects.get(id = id )
    if request.method == "POST":
        # If the request method is POST, update the status of the order item
        status = request.POST['status']
        cart_item.status= status
        cart_item.save()
    context = {
        'cart_item' : cart_item,
    }
    return render(request, "adminpanel/ordermanage.html", context)