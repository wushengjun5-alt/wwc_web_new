"""
Admin configuration for Products app
"""

from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
import csv
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='products_product_import_csv'),
            path('export-csv-template/', self.export_csv_template, name='products_product_export_template'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')

            if not csv_file:
                messages.error(request, 'Please upload a CSV file.')
                return redirect('..')

            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a CSV.')
                return redirect('..')

            try:
                # Parse CSV
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                created_count = 0
                updated_count = 0
                errors = []

                for row_num, row in enumerate(reader, start=2):  # start at 2 to account for header
                    try:
                        sku = row.get('sku', '').strip()
                        if not sku:
                            errors.append(f"Row {row_num}: SKU is required")
                            continue

                        # Get or create category
                        category_slug = row.get('category_slug', '').strip()
                        if not category_slug:
                            errors.append(f"Row {row_num}: category_slug is required")
                            continue

                        try:
                            category = ProductCategory.objects.get(slug=category_slug)
                        except ProductCategory.DoesNotExist:
                            errors.append(f"Row {row_num}: Category with slug '{category_slug}' not found")
                            continue

                        # Get producer if specified
                        producer = None
                        producer_slug = row.get('producer_slug', '').strip()
                        if producer_slug:
                            try:
                                producer = Producer.objects.get(slug=producer_slug)
                            except Producer.DoesNotExist:
                                errors.append(f"Row {row_num}: Producer with slug '{producer_slug}' not found (skipping producer)")

                        # Prepare product data
                        product_data = {
                            'name': row.get('name', '').strip(),
                            'sku': sku,
                            'category': category,
                            'producer': producer,
                            'description': row.get('description', '').strip(),
                            'price_tnd': float(row.get('price_tnd', 0)),
                            'impact_description': row.get('impact_description', '').strip(),
                            'impact_school': row.get('impact_school', '').strip(),
                            'impact_quantity': int(row.get('impact_quantity', 1)),
                            'impact_item': row.get('impact_item', '').strip(),
                        }

                        # Optional fields
                        if row.get('name_en'):
                            product_data['name_en'] = row['name_en'].strip()
                        if row.get('description_en'):
                            product_data['description_en'] = row['description_en'].strip()
                        if row.get('price_eur'):
                            product_data['price_eur'] = float(row['price_eur'])
                        if row.get('stock_quantity'):
                            product_data['stock_quantity'] = int(row['stock_quantity'])
                        if row.get('short_description'):
                            product_data['short_description'] = row['short_description'].strip()
                        if row.get('weight'):
                            product_data['weight'] = float(row['weight'])

                        # Boolean fields
                        product_data['is_active'] = row.get('is_active', 'true').lower() in ['true', '1', 'yes']
                        product_data['is_featured'] = row.get('is_featured', 'false').lower() in ['true', '1', 'yes']
                        product_data['is_natural'] = row.get('is_natural', 'false').lower() in ['true', '1', 'yes']
                        product_data['is_organic'] = row.get('is_organic', 'false').lower() in ['true', '1', 'yes']
                        product_data['is_handmade'] = row.get('is_handmade', 'false').lower() in ['true', '1', 'yes']
                        product_data['is_vegan'] = row.get('is_vegan', 'false').lower() in ['true', '1', 'yes']

                        # Create or update product
                        product, created = Product.objects.update_or_create(
                            sku=sku,
                            defaults=product_data
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

                # Show results
                if created_count > 0:
                    messages.success(request, f'Successfully created {created_count} products.')
                if updated_count > 0:
                    messages.success(request, f'Successfully updated {updated_count} products.')
                if errors:
                    for error in errors[:10]:  # Show first 10 errors
                        messages.error(request, error)
                    if len(errors) > 10:
                        messages.warning(request, f'And {len(errors) - 10} more errors...')

                return redirect('..')

            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
                return redirect('..')

        return render(request, 'admin/products/product/import_csv.html')

    def export_csv_template(self, request):
        """Export a CSV template with column headers and example data"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_import_template.csv"'

        writer = csv.writer(response)

        # Headers
        writer.writerow([
            'sku', 'name', 'name_en', 'category_slug', 'producer_slug',
            'description', 'description_en', 'short_description',
            'price_tnd', 'price_eur', 'stock_quantity', 'weight',
            'impact_description', 'impact_school', 'impact_quantity', 'impact_item',
            'is_active', 'is_featured', 'is_natural', 'is_organic', 'is_handmade', 'is_vegan'
        ])

        # Example row
        writer.writerow([
            'PROD-001', 'Roll-on Calme', 'Calm Roll-on', 'soins', 'farm-sidi',
            'Un roll-on apaisant naturel', 'A natural calming roll-on', 'Roll-on for relaxation',
            '25.00', '3.50', '100', '50',
            '6 barres energetiques fournies aux enfants', 'Sidi Mechreg', '6', 'barres energetiques',
            'true', 'false', 'true', 'true', 'true', 'false'
        ])

        return response

    change_list_template = 'admin/products/product/change_list.html'


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
