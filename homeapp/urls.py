from django.urls import path
from homeapp import views


urlpatterns = [
    path('',views.index,name="index"),
    # path('shop',views.shop,name="shop"),
]
