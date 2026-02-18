from django.urls import path
from .views import nagad_payment, order_complete

app_name = 'nagad'

urlpatterns = [
    path('pay/<str:order_number>/', nagad_payment, name='pay_with_nagad'),  # <-- এখানে ঠিক নাম দিন
    path('order_complete/', order_complete, name='order_complete'),
]
