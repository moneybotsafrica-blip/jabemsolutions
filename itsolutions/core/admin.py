from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum, F
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SiteStats, SiteContent, ContactMessage


class CustomAdminSite(AdminSite):
    site_header = _("Jabem Solutions Admin")
    site_title = _("Jabem Solutions Portal")
    index_title = _("Welcome to Jabem Solutions Administration")
    
    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        
        # Reorder apps for better organization
        desired_order = ['catalog', 'accounts', 'core']
        sorted_app_list = []
        
        for app in desired_order:
            for item in app_list:
                if item['app_label'] == app:
                    sorted_app_list.append(item)
                    break
        
        # Add any remaining apps
        for item in app_list:
            if item not in sorted_app_list:
                sorted_app_list.append(item)
        
        return sorted_app_list


custom_admin_site = CustomAdminSite(name='custom_admin')


# Dashboard Statistics
class DashboardStats:
    @staticmethod
    def get_stats():
        from catalog.models import Product, Order, Stock
        from accounts.models import User
        
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_orders': Order.objects.count(),
            'total_users': User.objects.count(),
            'low_stock_items': Stock.objects.filter(
                quantity_on_hand__lte=F('product__reorder_level')
            ).count(),
            'total_revenue': Order.objects.aggregate(
                total=Sum('total')
            )['total'] or 0,
            'pending_orders': Order.objects.filter(status='pending').count(),
        }
        return stats


@admin.register(SiteStats)
class SiteStatsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'updated_at')
    readonly_fields = ('name', 'value', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'title', 'is_active', 'order', 'updated_at')
    list_filter = ('content_type', 'is_active')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} messages marked as read.")
    mark_as_read.short_description = "Mark as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} messages marked as unread.")
    mark_as_unread.short_description = "Mark as unread"


# Register all models with custom admin site
from catalog.models import (
    Category, Brand, Product, Stock, StockMovement, 
    Cart, CartItem, Order, OrderItem,
    POSCategory, POSProduct, POSCustomer, POSSale, POSSaleItem
)
from catalog.admin import (
    CategoryAdmin, BrandAdmin, ProductAdmin, StockAdmin, StockMovementAdmin,
    CartAdmin, CartItemAdmin, OrderAdmin, OrderItemAdmin,
    POSCategoryAdmin, POSProductAdmin, POSCustomerAdmin, POSSaleAdmin, POSSaleItemAdmin
)
from accounts.models import User
from accounts.admin import UserAdmin

custom_admin_site.register(Category, CategoryAdmin)
custom_admin_site.register(Brand, BrandAdmin)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Stock, StockAdmin)
custom_admin_site.register(StockMovement, StockMovementAdmin)
custom_admin_site.register(Cart, CartAdmin)
custom_admin_site.register(CartItem, CartItemAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem, OrderItemAdmin)
custom_admin_site.register(POSCategory, POSCategoryAdmin)
custom_admin_site.register(POSProduct, POSProductAdmin)
custom_admin_site.register(POSCustomer, POSCustomerAdmin)
custom_admin_site.register(POSSale, POSSaleAdmin)
custom_admin_site.register(POSSaleItem, POSSaleItemAdmin)
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(SiteStats, SiteStatsAdmin)
custom_admin_site.register(SiteContent, SiteContentAdmin)
custom_admin_site.register(ContactMessage, ContactMessageAdmin)
