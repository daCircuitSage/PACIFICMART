from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from product.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True)
    context = {
        'products':products
    }
    return render(request, 'home.html', context)

def clear_messages(request):
    """Clear all messages from session"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Clear all messages
        storage = messages.get_messages(request)
        storage.used = True
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
