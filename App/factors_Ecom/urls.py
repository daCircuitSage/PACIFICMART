from django.contrib import admin

from django.urls import path, include

from .views import home

from django.conf import settings

from django.conf.urls.static import static



urlpatterns = [

    path('admin/', admin.site.urls),

    path('', home, name='home'),

    path('store/', include('product.urls')),

    path('cart/', include('cart.urls')),

    path('accounts/', include('accounts.urls')),

    #orders

    path('orders/', include('orders.urls')),



    path('bkash/', include('bkash.urls')),

    path('nagad/', include('nagad.urls')),

    path('cod/', include('cashOnDelevery.urls')),

]



# Only serve static files in development mode

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)