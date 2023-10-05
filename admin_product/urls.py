from django.urls import path
from . import views

urlpatterns = [
    path('products/',views.products, name='products'),
    path('addproduct/',views.add_product, name='addproduct'),
    path('product/editproduct/<int:id>/',views.edit_product, name='editproduct'),
    path('product/deleteproduct/<int:id>/',views.delete_product, name='deleteproduct'),
    path('addcategory/',views.add_category, name='addcategory'),
    path('editcategory/<int:id>/',views.edit_category, name='editcategory'),
    path('deletecategory/<int:id>/',views.delete_category, name='deletecategory'),
    path('addbrand/',views.add_brand, name='addbrand'),
    path('editbrand/<int:id>/',views.edit_brand, name='editbrand'),
    path('deletebrand/<int:id>/',views.delete_brand,name='deletebrand'),
    path('variant/<int:id>',views.variant,name='variant'),
    path('addvariant/',views.addvariant,name='addvariant'),
    path('editvariant/',views.editvariant,name='editvariant'),
]

