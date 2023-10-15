from . import views
from django.urls import path 

urlpatterns = [
    path('',views.place_order, name='placeorder'),
    path('payments/',views.payments, name='payments'),
    path('myorders/',views.my_orders, name='myorders'),
    path('cancelorder/<int:id>',views.cancel_orders, name='cancelorder'),
    path('presuccess/',views.pre_success, name='presuccess'),
    path('success/',views.success, name='success'),
    path('returnorder/<int:id>',views.return_order, name='returnorder'),
    path('wallet/',views.walletpayments, name='wallet'),
    path('my-wallet/',views.my_wallet, name='my-wallet'),
    
]