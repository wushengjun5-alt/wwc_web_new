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

class ProducerSerializer(serializers.ModelSerializer):
    """Serializer for product producers"""

    class Meta:
        model = Producer
        fields = [
            'id', 'name', 'slug', 'bio', 'location', 'photo',
            'total_products_sold', 'member_since', 'is_active'
        ]


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    has_children = serializers.ReadOnlyField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'name_en', 'name_ar', 'slug', 'description',
            'icon', 'image', 'parent', 'parent_name', 'order',
            'is_active', 'show_in_menu', 'has_children'
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category', 'category_name',
            'price_tnd', 'price_eur', 'compare_at_price_tnd', 'discount_percentage',
            'is_natural', 'is_organic', 'average_rating', 'review_count',
            'primary_image', 'is_in_stock', 'is_featured',
            'impact_quantity', 'impact_item', 'impact_school'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for product detail page"""
    category = ProductCategorySerializer(read_only=True)
    producer = ProducerSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_en', 'name_ar', 'slug', 'sku',
            'description', 'description_en', 'description_ar', 'short_description',
            'ingredients', 'ingredients_en', 'usage', 'usage_en',
            'category', 'producer', 'unit_type',
            'price_tnd', 'price_eur', 'compare_at_price_tnd', 'discount_percentage',
            'b2b_min_quantity', 'b2b_price_tnd', 'b2b_price_eur',
            'is_natural', 'is_organic', 'is_handmade', 'is_vegan', 'is_cruelty_free',
            'impact_description', 'impact_description_en', 'impact_description_ar',
            'impact_school', 'impact_quantity', 'impact_item', 'impact_item_en',
            'stock_quantity', 'is_in_stock', 'is_low_stock',
            'weight', 'dimensions',
            'average_rating', 'review_count',
            'images', 'is_active', 'is_featured',
            'created_at', 'updated_at'
        ]


class ComposableBoxSerializer(serializers.ModelSerializer):
    """Serializer for composable boxes"""
    eligible_products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = ComposableBox
        fields = [
            'id', 'name', 'name_en', 'slug', 'description', 'description_en',
            'image', 'min_items', 'max_items', 'price_tnd', 'price_eur',
            'eligible_products', 'is_active'
        ]


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
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    impact = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity',
            'subtotal', 'impact', 'added_at'
        ]

    def get_subtotal(self, obj):
        currency = self.context.get('currency', 'TND')
        return str(obj.get_subtotal(currency))

    def get_impact(self, obj):
        return obj.get_impact()


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
        choices=['stripe', 'bank_transfer', 'cash_on_delivery'],
        default='stripe'
    )

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
            'customer_type', 'phone', 'date_of_birth',
            'company_name', 'company_tax_id',
            'total_purchases', 'total_orders', 'total_impact_items', 'impact_breakdown',
            'preferred_currency', 'preferred_language',
            'newsletter_subscribed', 'created_at'
        ]
        read_only_fields = [
            'total_purchases', 'total_orders', 'total_impact_items',
            'impact_breakdown', 'created_at'
        ]


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

class ImpactEventSerializer(serializers.ModelSerializer):
    """Serializer for impact events"""

    class Meta:
        model = ImpactEvent
        fields = [
            'id', 'title', 'title_en', 'description', 'description_en',
            'school', 'date', 'items_delivered', 'item_type',
            'photo', 'video_url', 'is_published', 'created_at'
        ]


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
        if company_name:
            user.customer.company_name = company_name
        user.customer.save()

        return user
