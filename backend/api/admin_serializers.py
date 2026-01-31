"""
Admin Serializers for WWC Shop Product Management

These serializers provide full CRUD capabilities for the WordPress admin interface.
"""

from rest_framework import serializers
from django.utils.text import slugify
from products.models import Product, ProductImage, ProductCategory, Producer


class AdminProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images with full URL support"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class AdminCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight category serializer for dropdown selections"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'name_en', 'name_ar', 'slug', 'full_name', 'parent']

    def get_full_name(self, obj):
        """Return full category path (e.g., 'Parent > Child')"""
        if obj.parent:
            return f"{obj.parent.name} > {obj.name}"
        return obj.name


class AdminCategoryManageSerializer(serializers.ModelSerializer):
    """Full serializer for category management"""
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'name_en', 'name_ar', 'slug', 'description',
            'description_en', 'description_ar', 'icon', 'image', 'parent',
            'order', 'is_active', 'show_in_menu', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()

    def validate_slug(self, value):
        if value:
            from django.utils.text import slugify
            value = slugify(value)
            queryset = ProductCategory.objects.filter(slug=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ce slug existe déjà.")
        return value

    def validate(self, data):
        # Auto-generate slug if not provided
        if not data.get('slug') and data.get('name'):
            from django.utils.text import slugify
            base_slug = slugify(data['name'])
            slug = base_slug
            counter = 1
            while ProductCategory.objects.filter(slug=slug).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            data['slug'] = slug
        return data


class AdminProducerListSerializer(serializers.ModelSerializer):
    """Lightweight producer serializer for dropdown selections"""

    class Meta:
        model = Producer
        fields = ['id', 'name', 'slug', 'location']


class AdminProducerManageSerializer(serializers.ModelSerializer):
    """Full serializer for producer management"""
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Producer
        fields = [
            'id', 'name', 'slug', 'bio', 'location', 'image',
            'website', 'is_active', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'products_count']

    def get_products_count(self, obj):
        return obj.products.count()

    def validate_slug(self, value):
        if value:
            from django.utils.text import slugify
            value = slugify(value)
            queryset = Producer.objects.filter(slug=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ce slug existe déjà.")
        return value

    def validate(self, data):
        # Auto-generate slug if not provided
        if not data.get('slug') and data.get('name'):
            from django.utils.text import slugify
            base_slug = slugify(data['name'])
            slug = base_slug
            counter = 1
            while Producer.objects.filter(slug=slug).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            data['slug'] = slug
        return data


class AdminProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for product listing in admin table.
    Includes key info for filtering and display.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    producer_name = serializers.CharField(source='producer.name', read_only=True, allow_null=True)
    primary_image_url = serializers.SerializerMethodField()
    language_completeness = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_en', 'name_ar', 'slug', 'sku',
            'category', 'category_name', 'producer', 'producer_name',
            'price_tnd', 'price_eur', 'stock_quantity',
            'is_active', 'is_featured', 'status',
            'primary_image_url', 'language_completeness',
            'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]

    def get_primary_image_url(self, obj):
        primary = obj.primary_image
        if primary and primary.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def get_language_completeness(self, obj):
        """Return which languages have complete data"""
        completeness = {'fr': True, 'en': False, 'ar': False}

        # French is always required/complete if product exists
        # Check English
        if obj.name_en and obj.description_en:
            completeness['en'] = True

        # Check Arabic
        if obj.name_ar and obj.description_ar:
            completeness['ar'] = True

        return completeness

    def get_status(self, obj):
        """Return status label for display"""
        return 'published' if obj.is_active else 'draft'


class AdminProductDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for product editing in admin.
    Supports all fields including translations.
    """
    images = AdminProductImageSerializer(many=True, read_only=True)
    category_data = AdminCategoryListSerializer(source='category', read_only=True)
    producer_data = AdminProducerListSerializer(source='producer', read_only=True)
    impact_preview = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            # Basic Info
            'id', 'slug', 'sku',

            # Names (all languages)
            'name', 'name_en', 'name_ar',

            # Descriptions (all languages)
            'description', 'description_en', 'description_ar',
            'short_description',

            # Additional content
            'ingredients', 'ingredients_en',
            'usage', 'usage_en',

            # Categorization
            'category', 'category_data',
            'producer', 'producer_data',
            'unit_type',

            # Pricing
            'price_tnd', 'price_eur', 'compare_at_price_tnd',
            'b2b_min_quantity', 'b2b_price_tnd', 'b2b_price_eur',

            # Badges
            'is_natural', 'is_organic', 'is_handmade', 'is_vegan', 'is_cruelty_free',

            # Impact (all languages)
            'impact_description', 'impact_description_en', 'impact_description_ar',
            'impact_school', 'impact_quantity', 'impact_item', 'impact_item_en',
            'impact_preview',

            # Inventory
            'stock_quantity', 'track_inventory', 'low_stock_threshold', 'allow_backorder',

            # Attributes
            'weight', 'dimensions',

            # SEO
            'meta_title', 'meta_description',

            # Status
            'is_active', 'is_featured',

            # Ratings (read-only)
            'average_rating', 'review_count',

            # Images
            'images',

            # Timestamps
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'average_rating', 'review_count', 'created_at', 'updated_at']

    def get_impact_preview(self, obj):
        """Generate preview text for impact display"""
        if obj.impact_quantity and obj.impact_item and obj.impact_school:
            return f"{obj.impact_quantity} {obj.impact_item} pour {obj.impact_school}"
        return None


class AdminProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.
    Handles validation and auto-slug generation.
    """
    # Make optional fields explicitly optional
    description = serializers.CharField(required=False, allow_blank=True, default='')
    description_en = serializers.CharField(required=False, allow_blank=True, default='')
    description_ar = serializers.CharField(required=False, allow_blank=True, default='')
    short_description = serializers.CharField(required=False, allow_blank=True, default='')
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        required=False,
        allow_null=True
    )
    producer = serializers.PrimaryKeyRelatedField(
        queryset=Producer.objects.all(),
        required=False,
        allow_null=True
    )
    price_tnd = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
        default=0
    )

    class Meta:
        model = Product
        fields = [
            # Basic Info
            'slug', 'sku',

            # Names (all languages)
            'name', 'name_en', 'name_ar',

            # Descriptions (all languages)
            'description', 'description_en', 'description_ar',
            'short_description',

            # Additional content
            'ingredients', 'ingredients_en',
            'usage', 'usage_en',

            # Categorization
            'category', 'producer', 'unit_type',

            # Pricing
            'price_tnd', 'price_eur', 'compare_at_price_tnd',
            'b2b_min_quantity', 'b2b_price_tnd', 'b2b_price_eur',

            # Badges
            'is_natural', 'is_organic', 'is_handmade', 'is_vegan', 'is_cruelty_free',

            # Impact (all languages)
            'impact_description', 'impact_description_en', 'impact_description_ar',
            'impact_school', 'impact_quantity', 'impact_item', 'impact_item_en',

            # Inventory
            'stock_quantity', 'track_inventory', 'low_stock_threshold', 'allow_backorder',

            # Attributes
            'weight', 'dimensions',

            # SEO
            'meta_title', 'meta_description',

            # Status
            'is_active', 'is_featured',
        ]

    def validate_sku(self, value):
        """Ensure SKU is unique (case-insensitive)"""
        if value:
            value = value.upper().strip()
            queryset = Product.objects.filter(sku__iexact=value)

            # Exclude current instance when updating
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    "Ce SKU existe déjà. Veuillez en choisir un autre."
                )
        return value

    def validate_slug(self, value):
        """Ensure slug is unique"""
        if value:
            value = slugify(value)
            queryset = Product.objects.filter(slug=value)

            # Exclude current instance when updating
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError(
                    "Ce slug existe déjà. Veuillez en choisir un autre."
                )
        return value

    def validate_name(self, value):
        """French name is required"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Le nom en français est obligatoire."
            )
        return value.strip()

    def validate_price_tnd(self, value):
        """Price must be positive"""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Le prix doit être supérieur à 0."
            )
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Auto-generate slug from name if not provided
        if not data.get('slug') and data.get('name'):
            base_slug = slugify(data['name'])
            slug = base_slug
            counter = 1

            # Ensure unique slug
            while Product.objects.filter(slug=slug).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            data['slug'] = slug

        # Auto-generate SKU if not provided
        if not data.get('sku'):
            import uuid
            category = data.get('category')
            prefix = category.slug[:4].upper() if category and hasattr(category, 'slug') else 'PROD'
            data['sku'] = f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

        # Set default category if not provided (use first active category)
        if not data.get('category') and not self.instance:
            default_category = ProductCategory.objects.filter(is_active=True).first()
            if default_category:
                data['category'] = default_category

        # Ensure description has a default value
        if not data.get('description'):
            data['description'] = data.get('name', 'Nouveau produit')

        return data

    def create(self, validated_data):
        """Create new product with sensible defaults"""
        # Set defaults for optional fields
        if 'is_active' not in validated_data:
            validated_data['is_active'] = False  # Draft by default

        return super().create(validated_data)


class AdminProductImageUploadSerializer(serializers.Serializer):
    """Serializer for image upload"""
    image = serializers.ImageField()
    alt_text = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_primary = serializers.BooleanField(default=False)
    order = serializers.IntegerField(default=0)

    def create(self, validated_data):
        product = self.context.get('product')
        if not product:
            raise serializers.ValidationError("Product is required")

        # If this is marked as primary, unmark others
        if validated_data.get('is_primary', False):
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)

        # If no images exist, make this one primary
        if not product.images.exists():
            validated_data['is_primary'] = True

        return ProductImage.objects.create(product=product, **validated_data)


class AdminBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions on products"""
    action = serializers.ChoiceField(choices=['publish', 'unpublish', 'delete'])
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
