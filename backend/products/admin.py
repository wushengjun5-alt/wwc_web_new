"""
Admin configuration for Products app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Producer, ProductCategory, Product, ProductImage,
    ComposableBox, Review
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'is_active', 'total_products_sold', 'member_since']
    list_filter = ['is_active', 'location']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['total_products_sold', 'total_earnings', 'created_at', 'updated_at']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'is_active', 'show_in_menu']
    list_filter = ['is_active', 'show_in_menu', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'price_tnd', 'stock_quantity',
        'is_active', 'is_featured', 'average_rating_display'
    ]
    list_filter = [
        'is_active', 'is_featured', 'category', 'producer',
        'is_natural', 'is_organic', 'unit_type'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'review_count', 'created_at', 'updated_at']
    inlines = [ProductImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_en', 'name_ar', 'slug', 'sku', 'category', 'producer', 'unit_type')
        }),
        ('Description', {
            'fields': ('description', 'description_en', 'description_ar', 'short_description',
                      'ingredients', 'ingredients_en', 'usage', 'usage_en')
        }),
        ('Pricing - TND', {
            'fields': ('price_tnd', 'compare_at_price_tnd')
        }),
        ('Pricing - EUR', {
            'fields': ('price_eur',),
            'classes': ('collapse',)
        }),
        ('B2B Pricing', {
            'fields': ('b2b_min_quantity', 'b2b_price_tnd', 'b2b_price_eur'),
            'classes': ('collapse',)
        }),
        ('Badges & Certifications', {
            'fields': ('is_natural', 'is_organic', 'is_handmade', 'is_vegan', 'is_cruelty_free')
        }),
        ('Social Impact', {
            'fields': ('impact_description', 'impact_description_en', 'impact_description_ar',
                      'impact_school', 'impact_quantity', 'impact_item', 'impact_item_en'),
            'description': 'Define the social impact of purchasing this product'
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'track_inventory', 'low_stock_threshold', 'allow_backorder')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('average_rating', 'review_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def average_rating_display(self, obj):
        if obj.average_rating:
            stars = '★' * int(obj.average_rating) + '☆' * (5 - int(obj.average_rating))
            return format_html(
                '<span style="color: #ffc107;">{}</span> ({}/5)',
                stars, obj.average_rating
            )
        return '-'
    average_rating_display.short_description = 'Rating'


@admin.register(ComposableBox)
class ComposableBoxAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_items', 'max_items', 'price_tnd', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['eligible_products']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    raw_id_fields = ['product', 'user']
    readonly_fields = ['created_at', 'updated_at']

    actions = ['approve_reviews', 'unapprove_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Approve selected reviews'

    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_reviews.short_description = 'Unapprove selected reviews'
