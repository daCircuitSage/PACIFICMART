from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Payment, Order, OrderProduct
from product.models import Product
from cart.models import CartItems
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from factors_Ecom.validators import is_valid_bangladeshi_phone as bangladeshi_number
from factors_Ecom.utils import send_order_confirmation_email


def bkash_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.is_ordered:
        messages.info(request, "This order has already been submitted.")
        return redirect(reverse('bkash:order_complete') + f'?order_number={order.order_number}')

    if request.method == 'POST':
        bkash_number = request.POST.get('bkash_number')
        trx_id = request.POST.get('trx_id')

        if not (bangladeshi_number(bkash_number)) or not trx_id:
            messages.error(request, "Please provide both valid bKash number and Transaction ID.")
            return render(request, 'payments/bkash.html', {'order': order})

        payment = Payment.objects.create(
            user=order.user,
            payment_id=trx_id,
            payment_method='bKash',
            amount_paid=order.order_total,
            status='Pending',
        )

        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = CartItems.objects.filter(user=request.user)
        for item in cart_items:
            orderproduct = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.product_price,
                ordered=True
            )
            orderproduct.variations.set(item.variations.all())
            orderproduct.save()

            item.product.stock -= item.quantity
            item.product.save()

        CartItems.objects.filter(user=request.user).delete()

        # Send order confirmation email using Brevo
        try:
            send_order_confirmation_email(request.user, order)
        except Exception as e:
            # Log error but don't fail the order process
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send order confirmation email: {str(e)}")

        messages.success(request, "Payment submitted successfully! Waiting for verification.")
        # Redirect to invoice page with order_number
        return redirect(reverse('bkash:order_complete') + f'?order_number={order.order_number}')

    return render(request, 'payments/bkash.html', {'order': order})




def order_complete(request):
    order_number = request.GET.get('order_number')
    order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
    order_products = OrderProduct.objects.filter(order=order)

    subtotal = 0
    for item in order_products:
        subtotal += item.product_price * item.quantity

    context = {
        'order': order,
        'order_products': order_products,
        'subtotal': subtotal
    }
    return render(request, 'orders/order_complete.html', context)

