from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Payment, Order, OrderProduct
from cart.models import CartItems
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from factors_Ecom.validators import is_valid_bangladeshi_phone as bangladeshi_number


def cod_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.is_ordered:
        messages.info(request, "This order has already been submitted.")
        return redirect(reverse('cod:order_complete') + f'?order_number={order.order_number}')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        sender_number = request.POST.get('sender_number')
        transaction_id = request.POST.get('transaction_id')

        if not payment_method or not (bangladeshi_number(sender_number)) or not transaction_id:
            messages.error(request, "Please complete all payment details.")
            return redirect(request.path)

        payment = Payment.objects.create(
            user=order.user,
            payment_id=transaction_id,
            payment_method=f"COD - {payment_method}",
            amount_paid=order.tax,
            status='Pending',
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItems.objects.filter(user=request.user, is_active=True).select_related('product').prefetch_related('variations')
        for item in cart_items:
            order_product = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.product_price,
                ordered=True,
            )
            order_product.variations.set(item.variations.all())

            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        messages.success(
            request,
            "Cash on Delivery order placed successfully! Your order is under verification."
        )

        return redirect(reverse('cod:order_complete') + f'?order_number={order.order_number}')

    return render(request, 'payments/cod.html', {
        'order': order,
        'bkash_number': '01XXXXXXXXX',
        'nagad_number': '01YYYYYYYYY',
    })

def cod_order_complete(request):
    order_number = request.GET.get('order_number')
    order = get_object_or_404(Order.objects.select_related('user', 'payment'), order_number=order_number, is_ordered=True)
    order_products = OrderProduct.objects.filter(order=order).select_related('product').prefetch_related('variations')

    subtotal = sum(item.product_price * item.quantity for item in order_products)

    context = {
        'order': order,
        'order_products': order_products,
        'subtotal': subtotal
    }
    return render(request, 'orders/order_complete.html', context)