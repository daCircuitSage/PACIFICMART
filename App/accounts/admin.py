from django.contrib import admin
from .models import Account, UserProfile, Vendor
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

class AccountAdmin(UserAdmin):
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')
    list_display_links = ('email','first_name','last_name','username')
    search_fields = ('email',)
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(Account, AccountAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        # Handle case where profile_picture might not exist or be empty
        if object.profile_picture:
            return format_html('<img src="{}" width="30" style="border-radius:50%;">',  object.profile_picture.url)
        return "No image"
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

admin.site.register(UserProfile, UserProfileAdmin)


class VendorAdmin(admin.ModelAdmin):
    """Admin configuration for Vendor model"""
    
    def thumbnail_nid_front(self, obj):
        if obj.nid_card_front:
            return format_html('<img src="{}" width="50" style="border-radius:5%;">', obj.nid_card_front.url)
        return "No image"
    thumbnail_nid_front.short_description = 'NID Front'
    
    def thumbnail_nid_back(self, obj):
        if obj.nid_card_back:
            return format_html('<img src="{}" width="50" style="border-radius:5%;">', obj.nid_card_back.url)
        return "No image"
    thumbnail_nid_back.short_description = 'NID Back'
    
    list_display = (
        'business_name', 
        'user', 
        'business_category', 
        'status', 
        'is_active',
        'created_at',
        'thumbnail_nid_front',
        'thumbnail_nid_back'
    )
    list_display_links = ('business_name', 'user')
    list_filter = ('status', 'is_active', 'business_category', 'created_at')
    search_fields = ('business_name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'approved_at', 'rejected_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_category', 'business_description')
        }),
        ('Contact Information', {
            'fields': ('business_phone', 'business_email')
        }),
        ('Location Information', {
            'fields': ('store_location', 'store_city', 'store_state')
        }),
        ('NID Verification', {
            'fields': ('nid_card_front', 'nid_card_back')
        }),
        ('Status Information', {
            'fields': ('status', 'is_active', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'approved_at', 'rejected_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_vendors', 'reject_vendors']
    
    def approve_vendors(self, request, queryset):
        """Bulk approve vendors"""
        for vendor in queryset.filter(status='PENDING'):
            vendor.approve("Bulk approval by admin")
        self.message_user(request, f"{queryset.count()} vendors have been approved.")
    approve_vendors.short_description = "Approve selected vendors"
    
    def reject_vendors(self, request, queryset):
        """Bulk reject vendors"""
        for vendor in queryset.filter(status='PENDING'):
            vendor.reject("Bulk rejection by admin")
        self.message_user(request, f"{queryset.count()} vendors have been rejected.")
    reject_vendors.short_description = "Reject selected vendors"

admin.site.register(Vendor, VendorAdmin)
