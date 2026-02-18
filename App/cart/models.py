from django.db import models
from product.models import Product, Variation
from accounts.models import Account



class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    

class CartItems(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.product_price*self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"
    

class CheckoutDB(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_area = models.CharField(max_length=100, blank=True, null=True)

