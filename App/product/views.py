from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page, never_cache
from django.core.cache import cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import logging
from category.models import Category
from .models import Product, ReviewRating, ProductGallery
from orders.models import OrderProduct
from .forms import Reviewform, VendorProductForm, ProductApprovalForm
from cart.models import CartItems
from cart.views import _cart_id
from accounts.models import Vendor
from django.core.exceptions import PermissionDenied

@cache_page(60 * 15)  # Cache for 15 minutes
def store(request, category_slug=None):
    category = None

    # Use the new get_visible_products method to only show approved products
    products = Product.get_visible_products().select_related('product_category', 'vendor').order_by('id')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(product_category=category)

    paginator = Paginator(products, 3)  
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': products.count(),
        'category': category,
    }
    return render(request, 'store/store.html', context)


@never_cache
def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(
        Product.get_visible_products().select_related('product_category', 'vendor'),
        product_category__slug=category_slug,
        product_slug=product_slug
    )

    in_cart = CartItems.objects.filter(
        cart__cart_id=_cart_id(request),
        product=single_product
    ).exists()
    if request.user.is_authenticated:
        
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, 
        status=True
    ).select_related('user').order_by('-created_at')
    #get the product gallery here :
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id).select_related('product')

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery
    }
    return render(request, 'store/product_detail.html', context)


@cache_page(60 * 30)  # Cache for 30 minutes
def search(request):
    keyword = request.GET.get('keyword', '').strip()

    products = Product.get_visible_products()
    product_count = 0

    if keyword:
        products = (
            products
            .filter(
                Q(product_name__icontains=keyword) |
                Q(product_description__icontains=keyword)
            )
            .select_related('product_category', 'vendor')
            .order_by('-created_at')
        )
        product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        'keyword': keyword,
    }
    return render(request, 'store/store.html', context)





from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
@never_cache
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')

    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(
                user=request.user,
                product_id=product_id
            )
            form = Reviewform(request.POST, instance=review)
            if form.is_valid():
                # Ensure rating is float
                cleaned_data = form.cleaned_data
                cleaned_data['rating'] = float(cleaned_data.get('rating', 0))
                
                # Update and save
                review.rating = cleaned_data['rating']
                review.subject = cleaned_data.get('subject', '')
                review.review = cleaned_data.get('review', '')
                review.save()
                
                # Clear cache for this product
                cache.delete(f'product_detail_{product_id}')
                
                messages.success(request, f"Your review has been updated. Rating: {review.rating} stars")
            else:
                messages.error(request, f"Invalid review data. Errors: {form.errors}")
        except ReviewRating.DoesNotExist:
            form = Reviewform(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.product_id = product_id
                data.user = request.user
                data.ip = request.META.get('REMOTE_ADDR')
                
                # Ensure rating is float
                data.rating = float(data.rating)
                
                data.save()
                
                # Clear cache for this product
                cache.delete(f'product_detail_{product_id}')
                
                messages.success(request, f"Your review has been submitted successfully! Rating: {data.rating} stars")
            else:
                messages.error(request, f"Invalid review data. Errors: {form.errors}")

    return redirect(url or 'store')


# ================= VENDOR PRODUCT MANAGEMENT VIEWS =================

def is_vendor(user):
    """Check if user is a vendor"""
    return hasattr(user, 'vendor') and user.vendor is not None

def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.is_admin

@login_required(login_url='login')
@user_passes_test(is_vendor, login_url='vendor_register')
def vendor_product_create(request):
    """View for vendors to create new products"""
    vendor = request.user.vendor
    
    if not vendor.can_post_products():
        messages.error(request, 'Your vendor account is not active. Please wait for admin approval.')
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorProductForm(request.POST, request.FILES, vendor=vendor)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.vendor = vendor
                product.status = 'PENDING'  # Requires admin approval
                product.save()
                
                messages.success(request, 'Your product has been submitted for approval. It will be visible once approved by admin.')
                return redirect('vendor_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = VendorProductForm(vendor=vendor)
    
    return render(request, 'product/vendor_product_create.html', {
        'form': form,
        'vendor': vendor
    })

@login_required(login_url='login')
@user_passes_test(is_vendor, login_url='vendor_register')
def vendor_product_edit(request, product_id):
    """View for vendors to edit their products"""
    vendor = request.user.vendor
    
    if not vendor.can_post_products():
        messages.error(request, 'Your vendor account is not active.')
        return redirect('vendor_dashboard')
    
    product = get_object_or_404(Product, id=product_id, vendor=vendor)
    
    # Only allow editing pending products
    if product.status == 'APPROVED':
        messages.warning(request, 'You cannot edit approved products. Please contact admin for changes.')
        return redirect('vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorProductForm(request.POST, request.FILES, instance=product, vendor=vendor)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Product updated successfully.')
                return redirect('vendor_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
    else:
        form = VendorProductForm(instance=product, vendor=vendor)
    
    return render(request, 'product/vendor_product_edit.html', {
        'form': form,
        'product': product,
        'vendor': vendor
    })

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_product_list(request):
    """Admin view to list all products for approval"""
    products = Product.objects.all().select_related('vendor', 'product_category').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        products = products.filter(status=status_filter)
    
    # Filter by vendor if provided
    vendor_filter = request.GET.get('vendor')
    if vendor_filter:
        products = products.filter(vendor_id=vendor_filter)
    
    context = {
        'products': products,
        'status_filter': status_filter,
        'vendor_filter': vendor_filter,
        'vendors': Vendor.objects.all()
    }
    
    return render(request, 'product/admin_product_list.html', context)

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def admin_product_detail(request, product_id):
    """Admin view to review and approve/reject products"""
    product = get_object_or_404(Product.objects.select_related('vendor', 'product_category'), id=product_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        form = ProductApprovalForm(request.POST)
        
        if form.is_valid() and action in ['approve', 'reject']:
            rejection_reason = form.cleaned_data.get('rejection_reason', '')
            
            if action == 'approve':
                product.approve()
                messages.success(request, f'Product "{product.product_name}" has been approved.')
                
                # Send approval email to vendor
                if product.vendor:
                    send_product_status_email(product, 'approved')
                
            elif action == 'reject':
                product.reject(rejection_reason)
                messages.success(request, f'Product "{product.product_name}" has been rejected.')
                
                # Send rejection email to vendor
                if product.vendor:
                    send_product_status_email(product, 'rejected')
            
            return redirect('admin_product_list')
    else:
        form = ProductApprovalForm()
    
    return render(request, 'product/admin_product_detail.html', {
        'product': product,
        'form': form
    })

def send_product_status_email(product, status):
    """Send email to vendor about product status"""
    try:
        subject = f'Your Product Status - {status.title()}'
        
        template = 'product/product_approval_email.html' if status == 'approved' else 'product/product_rejection_email.html'
        
        message = render_to_string(template, {
            'product': product,
            'vendor': product.vendor,
            'status': status,
            'domain': 'thepacificmart.onrender.com'  # Update with actual domain
        })
        
        send_email = EmailMessage(
            subject=subject,
            body=message,
            from_email=f"{settings.BREVO_SENDER_NAME} <{settings.DEFAULT_FROM_EMAIL}>",
            to=[product.vendor.get_email()]
        )
        send_email.content_subtype = "html"
        send_email.send(fail_silently=False)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Product {status} email sent to {product.vendor.get_email()}")
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send product {status} email: {str(e)}")