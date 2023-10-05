from django.urls import path
from . import views

urlpatterns = [
    path('',views.wishlist,name='wishlist'),
    path('<int:id>/',views.add_wishlist,name = 'add_wishlist'),
    path('delete/<int:id>/',views.delete_wishlist,name='delete_wishlist')
]
