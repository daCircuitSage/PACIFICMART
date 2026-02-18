from django.urls import path
from . import views

app_name = 'bkash'  

urlpatterns = [
    path('pay/<str:order_number>/', views.bkash_payment, name='pay_with_bkash'),
    path('order_complete/', views.order_complete, name='order_complete'),

]
