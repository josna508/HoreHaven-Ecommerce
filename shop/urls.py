from . import views
from django.urls import path 

urlpatterns = [
    path('',views.shop, name='shop'),
    path('view/<int:id>/',views.product_details, name='product_details'),
    path('search_result/', views.search_result, name='search_result'),
    path('filtered-product/', views.filtered_products, name='filtered_products'),

]
