from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('images')
class ProductGellyInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'product_slug':('product_name',)}
    list_display = ('product_name','product_slug', 'product_price','is_available','created_at','updated_at')
    search_fields = ('product_name',)
    inlines = [ProductGellyInline]

admin.site.register(Product, ProductAdmin)

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category', 'variation_value','is_active','created_at')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category', 'variation_value','is_active')
admin.site.register(Variation, VariationAdmin)

admin.site.register(ReviewRating)


admin.site.register(ProductGallery)

