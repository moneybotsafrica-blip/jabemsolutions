from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Category, Brand, Product, Stock, StockMovement, Cart, CartItem, Order, OrderItem,
    POSCategory, POSProduct, POSCustomer, POSSale, POSSaleItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "slug", "description")
    list_filter = ("kind",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("logo_preview", "name",)
    search_fields = ("name",)
    
    def logo_preview(self, obj):
        if obj.get_logo_url():
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.get_logo_url())
        return format_html('<span style="color: #999;">No logo</span>')
    logo_preview.short_description = "Logo"


class StockInline(admin.StackedInline):
    model = Stock
    extra = 0
    readonly_fields = ("updated_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview", "name", "sku", "category", "brand", "product_type",
        "price", "stock_badge", "stock_status", "is_active",
    )
    list_filter = ("product_type", "category", "brand", "is_active", "track_inventory")
    search_fields = ("name", "sku", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [StockInline]
    actions = ['bulk_enable_tracking', 'bulk_disable_tracking', 'bulk_set_reorder_level']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'brand', 'product_type')
        }),
        ('Pricing & Description', {
            'fields': ('price', 'short_description', 'description')
        }),
        ('Images', {
            'fields': ('image', 'external_image_url'),
            'description': 'Use external_image_url for Vercel deployment or external hosting'
        }),
        ('Inventory Settings', {
            'fields': ('is_active', 'track_inventory', 'reorder_level')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def image_preview(self, obj):
        if obj.get_image_url():
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />', obj.get_image_url())
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = "Image"

    def stock_badge(self, obj):
        if not obj.track_inventory:
            return "—"
        qty = obj.quantity_on_hand
        color = "#c0392b" if obj.is_low_stock else "#27ae60"
        return format_html('<b style="color:{}">{}</b>', color, qty)
    stock_badge.short_description = "On hand"
    
    def stock_status(self, obj):
        if not obj.track_inventory:
            return format_html('<span class="badge bg-secondary">Not Tracked</span>')
        if obj.quantity_on_hand <= 0:
            return format_html('<span class="badge bg-danger">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span class="badge bg-warning">Low Stock</span>')
        else:
            return format_html('<span class="badge bg-success">In Stock</span>')
    stock_status.short_description = "Status"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Ensure every trackable product has a Stock row.
        if obj.track_inventory and not hasattr(obj, "stock"):
            Stock.objects.create(product=obj, quantity_on_hand=0)
    
    def bulk_enable_tracking(self, request, queryset):
        updated = queryset.filter(track_inventory=False).update(track_inventory=True)
        from django.contrib import messages
        # Create stock records for products that don't have them
        for product in queryset.filter(track_inventory=True):
            if not hasattr(product, 'stock'):
                Stock.objects.create(product=product, quantity_on_hand=0)
        messages.success(request, f"{updated} products now have inventory tracking enabled.")
    bulk_enable_tracking.short_description = "Enable Inventory Tracking"
    
    def bulk_disable_tracking(self, request, queryset):
        updated = queryset.update(track_inventory=False)
        from django.contrib import messages
        messages.success(request, f"{updated} products now have inventory tracking disabled.")
    bulk_disable_tracking.short_description = "Disable Inventory Tracking"
    
    def bulk_set_reorder_level(self, request, queryset):
        from django.contrib import messages
        messages.info(request, "Please specify the reorder level in the next step.")
        request.session['bulk_reorder_ids'] = list(queryset.values_list('id', flat=True))
        return redirect('admin:bulk_reorder_level')
    bulk_set_reorder_level.short_description = "Set Reorder Level"


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity_on_hand", "warehouse_location", "updated_at", "stock_status", "reorder_level", "value_at_cost")
    search_fields = ("product__name", "product__sku", "warehouse_location")
    list_filter = ("warehouse_location", "product__category", "product__brand", "updated_at")
    list_editable = ("quantity_on_hand", "warehouse_location")
    readonly_fields = ("updated_at",)
    actions = ['mark_as_in_stock', 'mark_as_out_of_stock', 'set_low_stock_threshold', 'bulk_stock_adjustment', 'generate_inventory_report']
    
    fieldsets = (
        ('Stock Information', {
            'fields': ('product', 'quantity_on_hand', 'warehouse_location')
        }),
        ('Stock Actions', {
            'fields': (),
            'description': 'Use the admin actions below for bulk stock operations'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product', 'product__category', 'product__brand')
    
    def stock_status(self, obj):
        if obj.quantity_on_hand <= 0:
            return format_html('<span class="badge bg-danger">Out of Stock</span>')
        elif obj.quantity_on_hand <= obj.product.reorder_level:
            return format_html('<span class="badge bg-warning">Low Stock</span>')
        else:
            return format_html('<span class="badge bg-success">In Stock</span>')
    stock_status.short_description = "Status"
    
    def reorder_level(self, obj):
        return obj.product.reorder_level
    reorder_level.short_description = "Reorder Level"
    
    def value_at_cost(self, obj):
        # Assuming we might add cost price later, for now use retail price
        estimated_value = obj.quantity_on_hand * obj.product.price
        return format_html('KES {:,.0f}', estimated_value)
    value_at_cost.short_description = "Estimated Value"
    
    def mark_as_in_stock(self, request, queryset):
        updated = queryset.update(quantity_on_hand=50)
        from django.contrib import messages
        messages.success(request, f"{updated} items marked as in stock (set to 50 units).")
    mark_as_in_stock.short_description = "Mark as In Stock (50 units)"
    
    def mark_as_out_of_stock(self, request, queryset):
        updated = queryset.update(quantity_on_hand=0)
        from django.contrib import messages
        messages.success(request, f"{updated} items marked as out of stock.")
    mark_as_out_of_stock.short_description = "Mark as Out of Stock"
    
    def set_low_stock_threshold(self, request, queryset):
        updated = 0
        for stock in queryset:
            stock.quantity_on_hand = stock.product.reorder_level
            stock.save()
            updated += 1
        from django.contrib import messages
        messages.success(request, f"{updated} items set to low stock threshold.")
    set_low_stock_threshold.short_description = "Set to Low Stock Threshold"
    
    def bulk_stock_adjustment(self, request, queryset):
        from django.contrib import messages
        messages.info(request, f"Selected {queryset.count()} items for bulk adjustment. Please edit quantities individually or use other bulk actions.")
    bulk_stock_adjustment.short_description = "Bulk Stock Adjustment (Select for Editing)"
    
    def generate_inventory_report(self, request, queryset):
        from django.contrib import messages
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Product', 'SKU', 'Category', 'Quantity', 'Location', 'Unit Price', 'Total Value', 'Status'])
        
        for stock in queryset:
            status = "In Stock" if stock.quantity_on_hand > stock.product.reorder_level else "Low Stock" if stock.quantity_on_hand > 0 else "Out of Stock"
            total_value = stock.quantity_on_hand * stock.product.price
            writer.writerow([
                stock.product.name,
                stock.product.sku,
                stock.product.category.name if stock.product.category else 'N/A',
                stock.quantity_on_hand,
                stock.warehouse_location,
                stock.product.price,
                total_value,
                status
            ])
        
        messages.success(request, "Inventory report generated successfully.")
        return response
    generate_inventory_report.short_description = "Generate Inventory Report"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product", "movement_type", "quantity", "resulting_quantity",
        "reference", "created_by", "created_at",
    )
    list_filter = ("movement_type", "created_at")
    search_fields = ("product__name", "product__sku", "reference")
    readonly_fields = ("resulting_quantity", "created_at")

    def has_change_permission(self, request, obj=None):
        # Movements are an audit trail — don't allow editing history.
        return False


class CartItemInline(admin.StackedInline):
    model = CartItem
    extra = 0
    readonly_fields = ("added_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "total_price", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price", "added_at")
    list_filter = ("added_at",)
    search_fields = ("product__name", "cart__user__username")


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("price",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "total_items", "created_at", "order_actions")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "id", "full_name", "phone")
    readonly_fields = ("created_at", "updated_at", "subtotal", "shipping_cost", "total")
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled', 'generate_order_report']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'email', 'phone', 'address', 'city')
        }),
        ('Order Items', {
            'fields': (),
            'description': 'Order items are managed in the inline below'
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'total')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
    
    def order_actions(self, obj):
        return format_html(
            '<a href="{}" class="button">View Details</a>',
            reverse('admin:catalog_order_change', args=[obj.id])
        )
    order_actions.short_description = "Actions"
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        from django.contrib import messages
        messages.success(request, f"{updated} orders marked as processing.")
    mark_as_processing.short_description = "Mark as Processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'processing']).update(status='shipped')
        from django.contrib import messages
        messages.success(request, f"{updated} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status__in=['pending', 'processing', 'shipped']).update(status='delivered')
        from django.contrib import messages
        messages.success(request, f"{updated} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark as Delivered"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.exclude(status='cancelled').update(status='cancelled')
        from django.contrib import messages
        messages.success(request, f"{updated} orders marked as cancelled.")
    mark_as_cancelled.short_description = "Mark as Cancelled"
    
    def generate_order_report(self, request, queryset):
        from django.contrib import messages
        from django.http import HttpResponse
        import csv
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="orders_report_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Customer', 'Email', 'Phone', 'Status', 'Total', 'Items', 'Created', 'Address', 'City'])
        
        for order in queryset:
            writer.writerow([
                order.id,
                order.full_name,
                order.email,
                order.phone,
                order.get_status_display(),
                order.total,
                order.total_items,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.address,
                order.city
            ])
        
        messages.success(request, "Order report generated successfully.")
        return response
    generate_order_report.short_description = "Generate Order Report"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "total_price")
    list_filter = ("order__status",)
    search_fields = ("product__name", "order__id")


# POS Demo Admin Classes
@admin.register(POSCategory)
class POSCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "order")


@admin.register(POSProduct)
class POSProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "price", "stock_quantity", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku", "description")
    list_editable = ("is_active", "order", "stock_quantity")


@admin.register(POSCustomer)
class POSCustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "total_orders", "total_spent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "email", "phone")
    list_editable = ("is_active",)


class POSSaleItemInline(admin.StackedInline):
    model = POSSaleItem
    extra = 0
    readonly_fields = ("total",)


@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer", "payment_method", "status", "total", "created_at")
    list_filter = ("payment_method", "status", "created_at")
    search_fields = ("order_id", "customer__name")
    readonly_fields = ("created_at", "created_by")
    inlines = [POSSaleItemInline]


@admin.register(POSSaleItem)
class POSSaleItemAdmin(admin.ModelAdmin):
    list_display = ("sale", "product", "quantity", "price", "total")
    list_filter = ("sale__status",)
    search_fields = ("product__name", "sale__order_id")
