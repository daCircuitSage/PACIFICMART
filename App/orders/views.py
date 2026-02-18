from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import datetime

from .models import Order, OrderProduct, Payment
from cart.models import Cart, CartItems, CheckoutDB
from .forms import OrderForm



def place_order(request, total=0, quantity=0):
    current_user = request.user

    # Check if user has items in cart
    cart_items = CartItems.objects.filter(user=current_user, is_active=True).select_related('product').prefetch_related('variations')
    if not cart_items.exists():
        return redirect('store')

    # Get delivery info from CheckoutDB
    checkout_data = CheckoutDB.objects.filter(user=current_user).last()
    if checkout_data:
        delivery_area = checkout_data.delivery_area
        delivery_charge = checkout_data.total_amount - sum([item.sub_total() for item in cart_items])
    else:
        delivery_area = "N/A"
        delivery_charge = 0

    # Calculate totals
    grand_total = 0
    total = 0
    quantity = 0
    for item in cart_items:
        total += item.sub_total()
        quantity += item.quantity
    grand_total = total + delivery_charge

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store order info
            order = Order()
            order.user = current_user
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address_line_1 = form.cleaned_data['address_line_1']
            order.address_line_2 = form.cleaned_data['address_line_2']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.order_note = form.cleaned_data.get('order_note', '')
            order.order_total = grand_total
            order.tax = delivery_charge  # delivery charge included as "tax"
            order.ip = request.META.get('REMOTE_ADDR')
            order.save()

            # Generate order number
            today = datetime.date.today()
            order_number = today.strftime("%Y%m%d") + str(order.id)
            order.order_number = order_number
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'delivery_charge': delivery_charge,
                'grand_total': grand_total,
                'delivery_area': delivery_area,
            }
             
            return render(request, 'orders/payments.html', context)
        else:
            # Add form errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            return redirect('checkout')
    else:
        return redirect('checkout')
