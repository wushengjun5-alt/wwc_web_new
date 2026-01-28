"""
Admin configuration for Orders app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem, ImpactEvent


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['added_at']
    raw_id_fields = ['product']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key_short', 'item_count', 'total', 'created_at']
    list_filter = ['currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]

    def session_key_short(self, obj):
        if obj.session_key:
            return f"{obj.session_key[:8]}..."
        return '-'
    session_key_short.short_description = 'Session'

    def item_count(self, obj):
        return obj.get_item_count()
    item_count.short_description = 'Items'

    def total(self, obj):
        return f"{obj.get_total()} {obj.currency}"
    total.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'subtotal', 'impact_quantity', 'impact_item']
    raw_id_fields = ['product', 'producer']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'email', 'status_badge', 'total_display',
        'payment_method', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at', 'shipping_country']
    search_fields = ['order_number', 'email', 'phone', 'user__username']
    readonly_fields = [
        'id', 'order_number', 'created_at', 'updated_at',
        'total_impact_items', 'impact_summary'
    ]
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'order_number', 'user', 'status', 'currency')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total')
        }),
        ('Social Impact', {
            'fields': ('total_impact_items', 'impact_summary'),
            'classes': ('collapse',)
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_first_name', 'shipping_last_name', 'shipping_company',
                'shipping_address_1', 'shipping_address_2', 'shipping_city',
                'shipping_state', 'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_same_as_shipping', 'billing_first_name', 'billing_last_name',
                'billing_company', 'billing_address_1', 'billing_address_2',
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_id', 'paid_at', 'coupon_code')
        }),
        ('Shipping', {
            'fields': ('shipping_method', 'tracking_number', 'shipped_at', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'processing': '#17a2b8',
            'shipped': '#6f42c1',
            'delivered': '#20c997',
            'cancelled': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_display(self, obj):
        return f"{obj.total} {obj.currency}"
    total_display.short_description = 'Total'

    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='paid', paid_at=timezone.now())
    mark_as_paid.short_description = 'Mark selected orders as paid'

    def mark_as_shipped(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='shipped', shipped_at=timezone.now())
    mark_as_shipped.short_description = 'Mark selected orders as shipped'

    def mark_as_delivered(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='delivered', delivered_at=timezone.now())
    mark_as_delivered.short_description = 'Mark selected orders as delivered'


@admin.register(ImpactEvent)
class ImpactEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'school', 'item_type', 'items_delivered', 'date', 'is_published']
    list_filter = ['is_published', 'school', 'item_type', 'date']
    search_fields = ['title', 'description', 'school']
    filter_horizontal = ['funded_by_orders']
    date_hierarchy = 'date'
