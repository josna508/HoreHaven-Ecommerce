from django.shortcuts import render, redirect
from user_profile.models import UserAddress
from cart.models import CartItem
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='handlelogin')
def checkout(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        sub_total = 0  # Initialize sub_total to zero

        # Calculate subtotals for each cart item
        for cart_item in cart_items:
            sub_total += cart_item.variant.price * cart_item.quantity

        # You can also calculate other values like shipping and handling here if needed
        shipping_and_handling = 0
        address = UserAddress.objects.filter(user=request.user)
        context = {
            'cart_items': cart_items,
            'sub_total': sub_total,
            'shipping_and_handling': shipping_and_handling,
            'addresses':address,
        }

        return render(request, "checkout.html", context)

    return redirect('handlelogin')
