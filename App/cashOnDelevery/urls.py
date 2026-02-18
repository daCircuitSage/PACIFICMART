from django.urls import path
from . import views

app_name = 'cod'  

urlpatterns = [
    path('pay/<str:order_number>/', views.cod_payment, name='pay_cod'),
    path('order_complete/', views.cod_order_complete, name='order_complete'),

]
