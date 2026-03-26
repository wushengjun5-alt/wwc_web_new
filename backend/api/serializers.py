"""
Serializers for WWC Shop REST API
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from products.models import (
    Producer, ProductCategory, Product, ProductImage,
    ComposableBox, Review
)
from orders.models import Cart, CartItem, Order, OrderItem, ImpactEvent
from customers.models import Customer, CustomerAddress, Wishlist


# ============================================
# Product Serializers
# ============================================

def _resolve_lang_field(obj_data_or_obj, base_field, lang, is_dict=False):
    """
    Return the best available value for a multilingual field.
    Tries <base_field>_<lang>, then falls back to <base_field>.
    Works on both model instances and plain dicts.
    """
    if lang and lang != 'fr':
        lang_field = f"{base_field}_{lang}"
        value = obj_data_or_obj.get(lang_field) if is_dict else getattr(obj_data_or_obj, lang_field, None)
        if value:
            return value
    return obj_data_or_obj.get(base_field) if is_dict else getattr(obj_data_or_obj, base_field, '')


class LangMixin:
    """Mixin that reads 'lang' from serializer context."""
    def get_lang(self):
        return self.context.get('lang', 'fr')


class ProducerSerializer(LangMixin, serializers.ModelSerializer):
    """Serializer for product producers"""
    bio = serializers.SerializerMethodField()

    class Meta:
        model = Producer
        fields = [
            'id', 'name', 'slug', 'bio', 'location', 'photo',
            'total_products_sold', 'member_since', 'is_active'
        ]

    def get_bio(self, obj):
        return _resolve_lang_field(obj, 'bio', self.get_lang())


class ProductCategorySerializer(LangMixin, serializers.ModelSerializer):
    """Serializer for product categories"""
    has_children = serializers.ReadOnlyField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'slug', 'description',
            'icon', 'image', 'parent', 'parent_name', 'order',
            'is_active', 'show_in_menu', 'has_children'
        ]

    def get_name(self, obj):
        return _resolve_lang_field(obj, 'name', self.get_lang())

    def get_description(self, obj):
        return _resolve_lang_field(obj, 'description', self.get_lang())


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']

    def get_image(self, obj):
        # If stored value is already an absolute URL (e.g. placeholder), return as-is
        val = str(obj.image)
        if val.startswith('http://') or val.startswith('https://'):
            return val
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ProductListSerializer(LangMixin, serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
    category_name = serializers.SerializerMethodField()
    primary_image = ProductImageSerializer(read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    name = serializers.SerializerMethodField()
    impact_item = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category', 'category_name',
            'price_tnd', 'price_eur', 'compare_at_price_tnd', 'discount_percentage',
            'is_natural', 'is_organic', 'average_rating', 'review_count',
            'primary_image', 'is_in_stock', 'is_featured',
            'impact_quantity', 'impact_item', 'impact_school'
        ]

    def get_name(self, obj):
        return _resolve_lang_field(obj, 'name', self.get_lang())

    def get_category_name(self, obj):
        if not obj.category:
            return ''
        return _resolve_lang_field(obj.category, 'name', self.get_lang())

    def get_impact_item(self, obj):
        return _resolve_lang_field(obj, 'impact_item', self.get_lang())


class ProductDetailSerializer(LangMixin, serializers.ModelSerializer):
    """Full serializer for product detail page"""
    category = serializers.SerializerMethodField()
    producer = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    usage = serializers.SerializerMethodField()
    impact_description = serializers.SerializerMethodField()
    impact_item = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku',
            'description', 'short_description',
            'ingredients', 'usage',
            'category', 'producer', 'unit_type',
            'price_tnd', 'price_eur', 'compare_at_price_tnd', 'discount_percentage',
            'b2b_min_quantity', 'b2b_price_tnd', 'b2b_price_eur',
            'is_natural', 'is_organic', 'is_handmade', 'is_vegan', 'is_cruelty_free',
            'impact_description', 'impact_school', 'impact_quantity', 'impact_item',
            'stock_quantity', 'is_in_stock', 'is_low_stock',
            'weight', 'dimensions',
            'average_rating', 'review_count',
            'images', 'is_active', 'is_featured',
            'created_at', 'updated_at'
        ]

    def get_name(self, obj):
        return _resolve_lang_field(obj, 'name', self.get_lang())

    def get_description(self, obj):
        return _resolve_lang_field(obj, 'description', self.get_lang())

    def get_ingredients(self, obj):
        return _resolve_lang_field(obj, 'ingredients', self.get_lang())

    def get_usage(self, obj):
        return _resolve_lang_field(obj, 'usage', self.get_lang())

    def get_impact_description(self, obj):
        return _resolve_lang_field(obj, 'impact_description', self.get_lang())

    def get_impact_item(self, obj):
        return _resolve_lang_field(obj, 'impact_item', self.get_lang())

    def get_category(self, obj):
        if not obj.category:
            return None
        return ProductCategorySerializer(obj.category, context=self.context).data

    def get_producer(self, obj):
        if not obj.producer:
            return None
        return ProducerSerializer(obj.producer, context=self.context).data


class ComposableBoxSerializer(LangMixin, serializers.ModelSerializer):
    """Serializer for composable boxes"""
    eligible_products = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = ComposableBox
        fields = [
            'id', 'name', 'slug', 'description',
            'image', 'min_items', 'max_items', 'price_tnd', 'price_eur',
            'eligible_products', 'is_active'
        ]

    def get_name(self, obj):
        return _resolve_lang_field(obj, 'name', self.get_lang())

    def get_description(self, obj):
        return _resolve_lang_field(obj, 'description', self.get_lang())

    def get_eligible_products(self, obj):
        return ProductListSerializer(obj.eligible_products.all(), many=True, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'rating', 'title', 'comment', 'user_name',
            'is_verified_purchase', 'helpful_votes', 'created_at'
        ]
        read_only_fields = ['user_name', 'is_verified_purchase', 'helpful_votes']

    def get_user_name(self, obj):
        # Return first name or masked email for privacy
        if obj.user.first_name:
            return obj.user.first_name
        email = obj.user.email
        return email.split('@')[0][:3] + '***'


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""

    class Meta:
        model = Review
        fields = ['product', 'rating', 'title', 'comment']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# ============================================
# Cart Serializers
# ============================================

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)
    subtotal = serializers.SerializerMethodField()
    impact = serializers.SerializerMethodField()
    composable_box_name = serializers.CharField(source='composable_box.name', read_only=True)
    composable_box_slug = serializers.CharField(source='composable_box.slug', read_only=True)
    composable_box_image = serializers.SerializerMethodField()
    composable_box_price_tnd = serializers.DecimalField(
        source='composable_box.price_tnd', max_digits=10, decimal_places=2, read_only=True
    )
    composable_box_price_eur = serializers.DecimalField(
        source='composable_box.price_eur', max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity',
            'composable_box_name', 'composable_box_slug', 'composable_box_image',
            'composable_box_price_tnd', 'composable_box_price_eur', 'box_items',
            'subtotal', 'impact', 'added_at'
        ]

    def get_subtotal(self, obj):
        currency = self.context.get('currency', 'TND')
        return str(obj.get_subtotal(currency))

    def get_impact(self, obj):
        return obj.get_impact()

    def get_composable_box_image(self, obj):
        if not obj.composable_box or not obj.composable_box.image:
            return None
        val = str(obj.composable_box.image)
        if val.startswith('http://') or val.startswith('https://'):
            return val
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.composable_box.image.url)
        return obj.composable_box.image.url


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    total_impact = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'currency', 'items', 'total', 'item_count',
            'total_impact', 'created_at', 'updated_at'
        ]

    def get_total(self, obj):
        return str(obj.get_total())

    def get_item_count(self, obj):
        return obj.get_item_count()

    def get_total_impact(self, obj):
        return obj.get_total_impact()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=0)


class AddBoxToCartSerializer(serializers.Serializer):
    """Serializer for adding a composable box to cart"""
    box_slug = serializers.SlugField()
    product_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        from products.models import ComposableBox, Product
        try:
            box = ComposableBox.objects.get(slug=data['box_slug'], is_active=True)
        except ComposableBox.DoesNotExist:
            raise serializers.ValidationError({'box_slug': 'Box not found'})

        product_ids = data['product_ids']
        if len(product_ids) < box.min_items:
            raise serializers.ValidationError(
                f'Minimum {box.min_items} items required for this box'
            )
        if len(product_ids) > box.max_items:
            raise serializers.ValidationError(
                f'Maximum {box.max_items} items allowed for this box'
            )

        eligible_ids = set(box.eligible_products.values_list('id', flat=True))
        invalid = [pid for pid in product_ids if pid not in eligible_ids]
        if invalid:
            raise serializers.ValidationError(
                f'Products {invalid} are not eligible for this box'
            )

        data['box'] = box
        return data


# ============================================
# Order Serializers
# ============================================

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'subtotal',
            'impact_quantity', 'impact_item', 'impact_school'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order listings"""
    item_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'currency',
            'total', 'item_count', 'total_impact_items', 'created_at'
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full serializer for order details"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 'currency',
            'subtotal', 'discount_amount', 'coupon_code', 'shipping_cost', 'tax_amount', 'total',
            'total_impact_items', 'impact_summary',
            'shipping_first_name', 'shipping_last_name', 'shipping_company',
            'shipping_address_1', 'shipping_address_2', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country',
            'billing_same_as_shipping',
            'billing_first_name', 'billing_last_name', 'billing_company',
            'billing_address_1', 'billing_address_2', 'billing_city',
            'billing_postal_code', 'billing_country',
            'payment_method', 'paid_at',
            'shipping_method', 'tracking_number', 'shipped_at', 'delivered_at',
            'customer_notes', 'items', 'created_at', 'updated_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout process"""
    # Contact
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)

    # Shipping address
    shipping_first_name = serializers.CharField(max_length=100)
    shipping_last_name = serializers.CharField(max_length=100)
    shipping_company = serializers.CharField(max_length=200, required=False, allow_blank=True)
    shipping_address_1 = serializers.CharField(max_length=200)
    shipping_address_2 = serializers.CharField(max_length=200, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=2, default='TN')

    # Payment — Stripe for all currencies; customer's bank handles conversion
    payment_method = serializers.ChoiceField(
        choices=['stripe', 'cash_on_delivery'],
        default='stripe'
    )

    # Billing address
    billing_same_as_shipping = serializers.BooleanField(required=False, default=True)
    billing_first_name  = serializers.CharField(required=False, allow_blank=True)
    billing_last_name   = serializers.CharField(required=False, allow_blank=True)
    billing_company     = serializers.CharField(required=False, allow_blank=True)
    billing_address_1   = serializers.CharField(required=False, allow_blank=True)
    billing_address_2   = serializers.CharField(required=False, allow_blank=True)
    billing_city        = serializers.CharField(required=False, allow_blank=True)
    billing_postal_code = serializers.CharField(required=False, allow_blank=True)
    billing_country     = serializers.CharField(max_length=2, required=False, allow_blank=True)

    # Optional
    customer_notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    gift_packaging = serializers.BooleanField(required=False, default=False)


# ============================================
# Customer Serializers
# ============================================

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer profile"""
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'customer_type', 'b2b_status', 'phone', 'date_of_birth',
            'company_name', 'company_tax_id',
            'default_shipping_first_name', 'default_shipping_last_name',
            'default_shipping_address_1', 'default_shipping_address_2',
            'default_shipping_city', 'default_shipping_state',
            'default_shipping_postal_code', 'default_shipping_country',
            'total_purchases', 'total_orders', 'total_impact_items', 'impact_breakdown',
            'preferred_currency', 'preferred_language',
            'newsletter_subscribed', 'created_at'
        ]
        read_only_fields = [
            'total_purchases', 'total_orders', 'total_impact_items',
            'impact_breakdown', 'created_at'
        ]

    def update(self, instance, validated_data):
        # Handle user fields (first_name, last_name)
        user_data = validated_data.pop('user', {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save(update_fields=list(user_data.keys()))
        return super().update(instance, validated_data)


class CustomerAddressSerializer(serializers.ModelSerializer):
    """Serializer for customer addresses"""
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'is_default',
            'first_name', 'last_name', 'company',
            'address_1', 'address_2', 'city', 'state',
            'postal_code', 'country', 'phone', 'full_address'
        ]


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']


class CustomerDashboardSerializer(serializers.Serializer):
    """Serializer for customer dashboard data"""
    customer = CustomerSerializer()
    recent_orders = OrderListSerializer(many=True)
    wishlist = WishlistSerializer(many=True)
    impact_summary = serializers.DictField()


# ============================================
# Impact Serializers
# ============================================

class ImpactEventSerializer(LangMixin, serializers.ModelSerializer):
    """Serializer for impact events"""
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = ImpactEvent
        fields = [
            'id', 'title', 'description',
            'school', 'date', 'items_delivered', 'item_type',
            'photo', 'video_url', 'is_published', 'created_at'
        ]

    def get_title(self, obj):
        return _resolve_lang_field(obj, 'title', self.get_lang())

    def get_description(self, obj):
        return _resolve_lang_field(obj, 'description', self.get_lang())


# ============================================
# Auth Serializers
# ============================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    customer_type = serializers.ChoiceField(
        choices=['individual', 'company'],
        default='individual'
    )
    company_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name',
            'customer_type', 'company_name'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value

    def create(self, validated_data):
        customer_type = validated_data.pop('customer_type', 'individual')
        company_name = validated_data.pop('company_name', '')
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Update customer profile
        user.customer.customer_type = customer_type
        if customer_type == 'company':
            user.customer.b2b_status = 'pending_approval'
        if company_name:
            user.customer.company_name = company_name
        user.customer.save()

        return user
