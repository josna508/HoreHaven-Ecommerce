from django.urls import path
from . import views

urlpatterns = [

path('admin_dashbord/',views.admin_dashboard,name='adminpanel'),
path('signout/', views.signout, name = 'signout'),
path('userdetails/', views.user_details, name = 'userdetails'),
path('useraction/<int:id>', views.user_action, name = 'useraction'),
path('search_users/', views.search_users, name = 'searchusers'),
path('sales/', views.sales_report, name = 'sales'),
]