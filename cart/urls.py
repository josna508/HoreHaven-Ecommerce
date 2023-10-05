from django.urls import path
from . import views

urlpatterns = [
    path('',views.cart, name='cart'),
    path('addcart/<int:variant_id>/',views.add_cart, name='addcart'),
    path('removecart/<int:product_id>/',views.remove_cart, name='removecart'),  
    path('deletecart/<int:cartItem_id>/',views.delete_cart, name='deletecart'),
    # path('updatecart/<int:product_id>/',views.update_cart,name="updatecart")
]
