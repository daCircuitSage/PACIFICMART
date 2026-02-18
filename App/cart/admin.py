from django.contrib import admin
from .models import Cart, CartItems, CheckoutDB


class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'created_at', 'item_count']
    search_fields = ['cart_id']
    readonly_fields = ['created_at']
    
    def item_count(self, obj):
        return obj.cartitems_set.count()
    item_count.short_description = 'Items'


class CartItemsAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'get_cart_or_user', 'get_variations']
    list_filter = ['is_active', 'product']
    search_fields = ['product__product_name', 'user__email', 'cart__cart_id']
    readonly_fields = ['product']
    
    def get_cart_or_user(self, obj):
        if obj.user:
            return f"User: {obj.user.email}"
        elif obj.cart:
            return f"Cart: {obj.cart.cart_id}"
        return "N/A"
    get_cart_or_user.short_description = 'Cart/User'
    
    def get_variations(self, obj):
        return ", ".join([f"{v.variation_category}: {v.variation_value}" for v in obj.variations.all()])
    get_variations.short_description = 'Variations'


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItems, CartItemsAdmin)
admin.site.register(CheckoutDB)
