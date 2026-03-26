"""
Admin configuration for Customers app
"""

from django.contrib import admin
from django.db.models import Count, Sum, Q
from django.utils.html import format_html
from .models import Customer, CustomerAddress, Wishlist

CONFIRMED_STATUSES = ['paid', 'processing', 'shipped', 'delivered']


class CustomerAddressInline(admin.TabularInline):
    model = CustomerAddress
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'customer_type_badge', 'company_name', 'live_total_orders',
        'live_total_purchases', 'total_impact_items', 'created_at'
    ]
    list_filter = ['customer_type', 'preferred_currency', 'preferred_language', 'newsletter_subscribed']
    search_fields = ['user__username', 'user__email', 'company_name', 'phone']
    readonly_fields = [
        'total_purchases', 'total_orders', 'total_impact_items',
        'impact_breakdown', 'created_at', 'updated_at'
    ]
    inlines = [CustomerAddressInline]

    fieldsets = (
        ('User', {
            'fields': ('user', 'customer_type', 'phone', 'date_of_birth')
        }),
        ('Company Information (B2B)', {
            'fields': ('company_name', 'company_tax_id', 'company_address', 'company_contact_name'),
            'classes': ('collapse',)
        }),
        ('Default Shipping Address', {
            'fields': (
                'default_shipping_address_1', 'default_shipping_address_2',
                'default_shipping_city', 'default_shipping_state',
                'default_shipping_postal_code', 'default_shipping_country'
            ),
            'classes': ('collapse',)
        }),
        ('Social Impact', {
            'fields': ('total_purchases', 'total_orders', 'total_impact_items', 'impact_breakdown'),
            'description': 'Cumulative impact from customer purchases'
        }),
        ('Preferences', {
            'fields': ('preferred_currency', 'preferred_language')
        }),
        ('Marketing', {
            'fields': ('newsletter_subscribed', 'accepts_marketing')
        }),
        ('Verification', {
            'fields': ('email_verified', 'phone_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_type_badge(self, obj):
        if obj.customer_type == 'company':
            return format_html(
                '<span style="background-color: #6f42c1; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">B2B</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">B2C</span>'
        )
    customer_type_badge.short_description = 'Type'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _live_orders=Count(
                'user__orders',
                filter=Q(user__orders__status__in=CONFIRMED_STATUSES),
                distinct=True,
            ),
            _live_purchases=Sum(
                'user__orders__total',
                filter=Q(user__orders__status__in=CONFIRMED_STATUSES),
            ),
        )

    def live_total_orders(self, obj):
        return getattr(obj, '_live_orders', 0) or 0
    live_total_orders.short_description = 'Commandes'
    live_total_orders.admin_order_field = '_live_orders'

    def live_total_purchases(self, obj):
        val = getattr(obj, '_live_purchases', 0) or 0
        return f"{val:.2f} {obj.preferred_currency}"
    live_total_purchases.short_description = 'Total achats'
    live_total_purchases.admin_order_field = '_live_purchases'

    actions = ['recalculate_impact']

    def recalculate_impact(self, request, queryset):
        for customer in queryset:
            customer.update_impact_stats()
        self.message_user(request, f"Recalculated impact for {queryset.count()} customers.")
    recalculate_impact.short_description = 'Recalculate impact statistics'


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'full_name', 'city', 'country', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'country']
    search_fields = ['customer__user__email', 'first_name', 'last_name', 'city']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['customer__user__email', 'product__name']
    raw_id_fields = ['customer', 'product']
