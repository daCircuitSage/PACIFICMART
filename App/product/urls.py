from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='category_list_slug'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),

    path('submit_review/<int:product_id>', views.submit_review, name='submit_review'),

    # Vendor Product URLs
    path('vendor/create/', views.vendor_product_create, name='vendor_product_create'),
    path('vendor/edit/<int:product_id>/', views.vendor_product_edit, name='vendor_product_edit'),
    
    # Admin Product URLs
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/products/<int:product_id>/', views.admin_product_detail, name='admin_product_detail'),
]

