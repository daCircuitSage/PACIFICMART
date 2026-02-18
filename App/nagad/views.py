from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Payment, Order, OrderProduct
from product.models import Product
from cart.models import CartItems
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from factors_Ecom.validators import is_valid_bangladeshi_phone as bangladeshi_number


def nagad_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if order.is_ordered:
        messages.info(request, "This order has already been submitted.")
        return redirect(reverse('Nagad:order_complete') + f'?order_number={order.order_number}')
    
    if request.method == "POST":
        nagad_number = request.POST.get('nagad_number')
        trx_id = request.POST.get('trx_id')

        if not (bangladeshi_number(nagad_number)) or not trx_id:
            messages.error(request, "Please provide both valid Nagad number and Transaction ID.")
            return render(request, 'payments/nagad.html', {'order': order})
        
        payment = Payment.objects.create(
            user=order.user,
            payment_id=trx_id,
            payment_method='nagad',
            amount_paid=order.order_total,
            status='Pending',
        )

        order.payment = payment
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

        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.content_subtype = "html"
        send_email.send()

        messages.success(request, "Payment submitted successfully! Waiting for verification.")
        # Redirect to invoice page with order_number
        return redirect(reverse('bkash:order_complete') + f'?order_number={order.order_number}')
    
    return render(request, 'payments/nagad.html', {'order': order})


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

