from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page, never_cache
from django.core.cache import cache
from category.models import Category
from .models import Product, ReviewRating, ProductGallery
from orders.models import OrderProduct
from .forms import Reviewform
from cart.models import CartItems
from cart.views import _cart_id


@cache_page(60 * 15)  # Cache for 15 minutes
def store(request, category_slug=None):
    category = None

    products = Product.objects.filter(is_available=True).select_related('product_category').order_by('id')

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
        Product.objects.select_related('product_category'),
        product_category__slug=category_slug,
        product_slug=product_slug,
        is_available=True
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

    products = Product.objects.none()
    product_count = 0

    if keyword:
        products = (
            Product.objects
            .filter(
                Q(product_name__icontains=keyword) |
                Q(product_description__icontains=keyword)
            )
            .select_related('product_category')
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