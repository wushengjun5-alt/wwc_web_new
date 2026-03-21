"""
Views for WWC Shop REST API
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """SessionAuthentication without CSRF enforcement — safe for API-only endpoints."""
    def enforce_csrf(self, request):
        return

from products.models import (
    Producer, ProductCategory, Product, ProductImage,
    ComposableBox, Review
)
from orders.models import Cart, CartItem, Order, OrderItem, ImpactEvent, Coupon
from customers.models import Customer, CustomerAddress, Wishlist

from .serializers import (
    ProducerSerializer, ProductCategorySerializer,
    ProductListSerializer, ProductDetailSerializer,
    ComposableBoxSerializer, ReviewSerializer, ReviewCreateSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    AddBoxToCartSerializer,
    OrderListSerializer, OrderDetailSerializer, CheckoutSerializer,
    CustomerSerializer, CustomerAddressSerializer, WishlistSerializer,
    CustomerDashboardSerializer, ImpactEventSerializer,
    UserRegistrationSerializer
)


# ============================================
# Product Views
# ============================================

class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for product categories"""
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter for menu categories only
        show_in_menu = self.request.query_params.get('menu', None)
        if show_in_menu:
            queryset = queryset.filter(show_in_menu=True)
        # Filter for parent categories only
        parent_only = self.request.query_params.get('parent_only', None)
        if parent_only:
            queryset = queryset.filter(parent__isnull=True)
        return queryset


class ProducerViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for producers"""
    queryset = Producer.objects.filter(is_active=True)
    serializer_class = ProducerSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products from a specific producer"""
        producer = self.get_object()
        products = Product.objects.filter(producer=producer, is_active=True)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    lookup_field = 'slug'
    # Note: 'category' removed from filterset_fields - we handle it manually by slug in get_queryset
    filterset_fields = ['producer', 'unit_type', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price_tnd', 'price_eur', 'created_at', 'average_rating', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category slug
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(
                Q(category__slug=category_slug) |
                Q(category__parent__slug=category_slug)
            )

        # Filter by badges
        is_natural = self.request.query_params.get('is_natural', None)
        if is_natural:
            queryset = queryset.filter(is_natural=True)

        is_organic = self.request.query_params.get('is_organic', None)
        if is_organic:
            queryset = queryset.filter(is_organic=True)

        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price_tnd__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_tnd__lte=max_price)

        # Filter in stock only
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock:
            queryset = queryset.filter(
                Q(track_inventory=False) |
                Q(stock_quantity__gt=0) |
                Q(allow_backorder=True)
            )

        return queryset.select_related('category', 'producer').prefetch_related('images')

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Get related products (same category)"""
        product = self.get_object()
        related = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        serializer = ProductListSerializer(related, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get product reviews"""
        product = self.get_object()
        reviews = Review.objects.filter(product=product, is_approved=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_review(self, request, slug=None):
        """Add a review to product"""
        product = self.get_object()
        data = request.data.copy()
        data['product'] = product.id

        serializer = ReviewCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComposableBoxViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for composable boxes"""
    queryset = ComposableBox.objects.filter(is_active=True)
    serializer_class = ComposableBoxSerializer
    lookup_field = 'slug'


# ============================================
# Cart Views
# ============================================

class CartViewSet(viewsets.ViewSet):
    """ViewSet for shopping cart operations"""
    permission_classes = [AllowAny]
    # Disable SessionAuthentication so CSRF is not enforced on POST requests
    # from the WordPress plugin. Cart identity uses X-Session-Key header instead.
    authentication_classes = []

    def get_cart(self, request):
        """Get or create cart for user/session.

        Identity priority:
        1. Authenticated user (JWT token in Authorization header)
        2. X-Session-Key header sent by the WP plugin (PHP session ID)
        3. Django session key as fallback
        """
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            # Merge any guest cart that shares the same session key
            session_key = request.META.get('HTTP_X_SESSION_KEY') or request.session.session_key
            if session_key:
                session_cart = Cart.objects.filter(session_key=session_key).first()
                if session_cart and session_cart != cart:
                    cart.merge_with(session_cart)
        else:
            # Use the PHP session key sent by the WP plugin, fall back to Django session
            session_key = request.META.get('HTTP_X_SESSION_KEY')
            if not session_key:
                if not request.session.session_key:
                    request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def list(self, request):
        """Get current cart"""
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, context={'currency': cart.currency})
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart(request)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = Product.objects.get(id=product_id)

        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        cart.refresh_from_db()
        return Response({
            'message': 'Product added to cart',
            'cart': CartSerializer(cart).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path='update/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """Update cart item quantity"""
        serializer = UpdateCartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart(request)
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = serializer.validated_data['quantity']
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'], url_path='remove/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """Remove item from cart"""
        cart = self.get_cart(request)
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart.refresh_from_db()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear entire cart"""
        cart = self.get_cart(request)
        cart.clear()
        return Response({'message': 'Cart cleared'})

    @action(detail=False, methods=['post'], url_path='add-box')
    def add_box(self, request):
        """Add a composable box to cart"""
        serializer = AddBoxToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart(request)
        box = serializer.validated_data['box']
        product_ids = serializer.validated_data['product_ids']
        quantity = serializer.validated_data['quantity']

        # Remove any existing box item for this box in cart, then create fresh
        CartItem.objects.filter(cart=cart, composable_box=box).delete()

        CartItem.objects.create(
            cart=cart,
            product=None,
            composable_box=box,
            box_items=product_ids,
            quantity=quantity,
        )

        cart.refresh_from_db()
        return Response({
            'message': 'Box added to cart',
            'cart': CartSerializer(cart, context={'currency': cart.currency}).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def impact(self, request):
        """Get total impact summary for cart"""
        cart = self.get_cart(request)
        return Response({
            'total_impact': cart.get_total_impact(),
            'item_count': cart.get_item_count()
        })

    @action(detail=False, methods=['post'], url_path='currency')
    def set_currency(self, request):
        """Set cart currency"""
        currency = request.data.get('currency', 'TND')
        if currency not in ['TND', 'EUR']:
            return Response(
                {'error': 'Invalid currency'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = self.get_cart(request)
        cart.currency = currency
        cart.save()
        return Response(CartSerializer(cart).data)


# ============================================
# Checkout Views
# ============================================

def _calculate_shipping(country, subtotal, currency):
    """
    Calculate shipping cost based on destination country and order subtotal.
    Mirrors the logic in WWC_Checkout::calculate_shipping() in the WP plugin.
    """
    rates = {'TN': 7.00, 'FR': 15.00, 'BE': 15.00, 'CH': 20.00, 'DE': 20.00}
    free_thresholds = {'TN': 100.00, 'FR': 50.00, 'BE': 50.00, 'CH': 75.00, 'DE': 75.00}

    threshold = free_thresholds.get(country, 75.00)
    if subtotal >= threshold:
        return 0.00
    return rates.get(country, 20.00)


class ApplyCouponView(APIView):
    """Validate a coupon code and return the discount amount"""
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        subtotal = request.data.get('subtotal', 0)
        try:
            subtotal = float(subtotal)
        except (ValueError, TypeError):
            subtotal = 0

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return Response({'error': 'Code promo invalide.'}, status=status.HTTP_400_BAD_REQUEST)

        valid, msg = coupon.is_valid(subtotal)
        if not valid:
            return Response({'error': msg}, status=status.HTTP_400_BAD_REQUEST)

        from decimal import Decimal
        discount = coupon.calculate_discount(Decimal(str(subtotal)))
        return Response({
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
        })


class CheckoutView(APIView):
    """Handle checkout process"""
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]

    def post(self, request):
        """Create order from cart"""
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()

        # Get cart — reuse CartViewSet logic so merging works for authenticated users
        cart = CartViewSet().get_cart(request)

        if not cart or cart.items.count() == 0:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        payment_method = data['payment_method']

        # Calculate totals
        subtotal = cart.get_total()
        country = data.get('shipping_country', 'TN')
        from decimal import Decimal
        shipping_cost = Decimal(str(_calculate_shipping(country, float(subtotal), cart.currency)))
        gift_packaging = data.get('gift_packaging', False)
        gift_packaging_fee = Decimal('0.00')
        if gift_packaging:
            gift_packaging_fee = Decimal('5.00') if cart.currency == 'TND' else Decimal('2.00')

        # Apply coupon discount
        coupon_code = data.get('coupon_code', '').strip().upper()
        discount_amount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                valid, _ = coupon.is_valid(float(subtotal))
                if valid:
                    discount_amount = coupon.calculate_discount(subtotal)
                    coupon.used_count += 1
                    coupon.save(update_fields=['used_count'])
            except Coupon.DoesNotExist:
                pass

        total = subtotal + shipping_cost + gift_packaging_fee - discount_amount

        # Calculate impact
        impact_summary = cart.get_total_impact()
        total_impact = sum(impact_summary.values())

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=data['email'],
            phone=data['phone'],
            status='pending',
            currency=cart.currency,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            tax_amount=gift_packaging_fee,
            total=total,
            total_impact_items=total_impact,
            impact_summary=impact_summary,
            shipping_first_name=data['shipping_first_name'],
            shipping_last_name=data['shipping_last_name'],
            shipping_company=data.get('shipping_company', ''),
            shipping_address_1=data['shipping_address_1'],
            shipping_address_2=data.get('shipping_address_2', ''),
            shipping_city=data['shipping_city'],
            shipping_state=data.get('shipping_state', ''),
            shipping_postal_code=data['shipping_postal_code'],
            shipping_country=data.get('shipping_country', 'TN'),
            payment_method=data['payment_method'],
            customer_notes=data.get('customer_notes', ''),
            coupon_code=data.get('coupon_code', ''),
        )

        # Create order items
        for cart_item in cart.items.all():
            product = cart_item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                producer=product.producer,
                product_name=product.name,
                product_sku=product.sku,
                quantity=cart_item.quantity,
                unit_price=product.get_price(cart.currency),
                subtotal=cart_item.get_subtotal(cart.currency),
                impact_quantity=product.impact_quantity * cart_item.quantity,
                impact_item=product.impact_item,
                impact_school=product.impact_school,
            )

            # Update stock
            if product.track_inventory:
                product.stock_quantity -= cart_item.quantity
                product.save()

        # Clear cart
        cart.clear()

        # For COD orders: mark as paid immediately and update customer impact
        if order.payment_method == 'cash_on_delivery':
            order.status = 'paid'
            order.save(update_fields=['status'])
            if order.user:
                order.user.customer.update_impact_stats()
            from .payments import _send_order_confirmation_email
            _send_order_confirmation_email(order)

        response_data = {
            'order_number': order.order_number,
            'order_id': str(order.id),
            'total': str(order.total),
            'currency': order.currency,
            'status': order.status,
            'payment_method': order.payment_method,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for orders"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    def get_object(self):
        """Allow lookup by order_number"""
        lookup = self.kwargs.get('pk')
        if lookup:
            return get_object_or_404(
                Order,
                order_number=lookup,
                user=self.request.user
            )
        return super().get_object()


# ============================================
# Customer Views
# ============================================

class CustomerDashboardView(APIView):
    """Customer dashboard with impact tracking"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user.customer

        # Get recent orders
        recent_orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        # Get wishlist
        wishlist = Wishlist.objects.filter(
            customer=customer
        ).select_related('product')[:10]

        # Calculate impact summary
        impact_summary = {
            'total_items': customer.total_impact_items,
            'breakdown': customer.impact_breakdown,
            'total_purchases': str(customer.total_purchases),
            'total_orders': customer.total_orders,
        }

        return Response({
            'customer': CustomerSerializer(customer).data,
            'recent_orders': OrderListSerializer(recent_orders, many=True).data,
            'wishlist': WishlistSerializer(wishlist, many=True).data,
            'impact_summary': impact_summary,
        })


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """View/update customer profile"""
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get_object(self):
        return self.request.user.customer


class CustomerAddressViewSet(viewsets.ModelViewSet):
    """ViewSet for customer addresses"""
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerAddressSerializer

    def get_queryset(self):
        return CustomerAddress.objects.filter(customer=self.request.user.customer)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet for wishlist"""
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(
            customer=self.request.user.customer
        ).select_related('product')

    def create(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            customer=request.user.customer,
            product=product
        )

        if created:
            return Response(
                WishlistSerializer(wishlist_item).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'message': 'Already in wishlist'},
            status=status.HTTP_200_OK
        )


# ============================================
# Impact Views
# ============================================

class ImpactEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for impact events"""
    queryset = ImpactEvent.objects.filter(is_published=True)
    serializer_class = ImpactEventSerializer
    filterset_fields = ['school', 'item_type']
    ordering_fields = ['date', 'items_delivered']


class ImpactSummaryView(APIView):
    """Global impact summary"""
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db.models import Sum

        # Total impact from all orders
        total_orders = Order.objects.filter(
            status__in=['paid', 'processing', 'shipped', 'delivered']
        )

        # Aggregate impact
        total_impact = total_orders.aggregate(
            total=Sum('total_impact_items')
        )['total'] or 0

        # Recent impact events
        recent_events = ImpactEvent.objects.filter(
            is_published=True
        ).order_by('-date')[:5]

        return Response({
            'total_impact_items': total_impact,
            'total_orders': total_orders.count(),
            'recent_events': ImpactEventSerializer(recent_events, many=True).data,
        })


# ============================================
# Auth Views
# ============================================

class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Issue JWT tokens immediately so the user is logged in after registration
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        # Merge guest cart if session key provided
        session_key = request.META.get('HTTP_X_SESSION_KEY')
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key).first()
            if guest_cart and guest_cart.items.exists():
                user_cart, _ = Cart.objects.get_or_create(user=user)
                user_cart.merge_with(guest_cart)

        return Response({
            'message': 'Inscription réussie',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """Login with email + password, returns JWT tokens"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from django.contrib.auth import authenticate
        from rest_framework_simplejwt.tokens import RefreshToken

        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {'error': 'Email et mot de passe requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Django username == email in this project
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {'error': 'Email ou mot de passe incorrect'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'Ce compte est désactivé'},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        # Merge guest cart on login
        session_key = request.META.get('HTTP_X_SESSION_KEY')
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key).first()
            if guest_cart and guest_cart.items.exists():
                user_cart, _ = Cart.objects.get_or_create(user=user)
                user_cart.merge_with(guest_cart)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'customer_type': user.customer.customer_type if hasattr(user, 'customer') else 'individual',
            }
        })


class PasswordResetRequestView(APIView):
    """Send password reset email"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from django.contrib.auth.models import User
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.core.mail import send_mail

        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)

        # Always return success to avoid email enumeration
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.SITE_URL}/shop/reset-password/?uid={uid}&token={token}"

            send_mail(
                subject='Réinitialisation de votre mot de passe - Wallah We Can',
                message=(
                    f"Bonjour {user.first_name},\n\n"
                    f"Cliquez sur ce lien pour réinitialiser votre mot de passe :\n{reset_url}\n\n"
                    "Ce lien est valable 24 heures.\n\n"
                    "Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.\n\n"
                    "L'équipe WWC"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Don't reveal whether email exists

        return Response({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé.'})


class PasswordResetConfirmView(APIView):
    """Confirm password reset with uid + token"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        from django.contrib.auth.models import User
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        password = request.data.get('password', '')
        password_confirm = request.data.get('password_confirm', '')

        if not all([uid, token, password, password_confirm]):
            return Response({'error': 'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)

        if password != password_confirm:
            return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({'error': 'Le mot de passe doit contenir au moins 8 caractères'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Lien invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Lien expiré ou invalide'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({'message': 'Mot de passe réinitialisé avec succès'})


# ============================================
# Donation Views
# ============================================

from donations.models import Country, DonationProject, Donation as DonationModel

class DonationCountryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        countries = Country.objects.filter(is_active=True)
        data = [{
            'id': c.id,
            'name': c.name,
            'name_en': c.name_en,
            'slug': c.slug,
            'flag_emoji': c.flag_emoji,
            'description': c.description,
            'project_count': c.projects.filter(is_active=True).count(),
        } for c in countries]
        return Response(data)


class DonationProjectListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = DonationProject.objects.filter(is_active=True).select_related('country')
        country_slug = request.query_params.get('country', '')
        if country_slug:
            queryset = queryset.filter(country__slug=country_slug)
        data = [{
            'id': p.id,
            'title': p.title,
            'title_en': p.title_en,
            'description': p.description,
            'school': p.school,
            'category': p.category,
            'goal_amount': str(p.goal_amount),
            'raised_amount': str(p.raised_amount),
            'progress_percent': p.progress_percent,
            'donor_count': p.donor_count,
            'currency': p.currency,
            'deadline': p.deadline.isoformat() if p.deadline else None,
            'image': request.build_absolute_uri(p.image.url) if p.image else None,
            'is_featured': p.is_featured,
            'country': {'name': p.country.name, 'slug': p.country.slug, 'flag_emoji': p.country.flag_emoji},
        } for p in queryset]
        return Response(data)


class DonationProjectDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        p = get_object_or_404(DonationProject, pk=pk, is_active=True)
        recent_donors = []
        for d in p.donations.filter(status='completed').order_by('-created_at')[:5]:
            recent_donors.append({
                'name': 'Anonyme' if d.is_anonymous else (d.donor_name or 'Donateur'),
                'amount': str(d.amount),
                'currency': d.currency,
                'message': d.message if not d.is_anonymous else '',
                'created_at': d.created_at.isoformat(),
            })
        return Response({
            'id': p.id,
            'title': p.title,
            'title_en': p.title_en,
            'description': p.description,
            'description_en': p.description_en,
            'school': p.school,
            'category': p.category,
            'goal_amount': str(p.goal_amount),
            'raised_amount': str(p.raised_amount),
            'progress_percent': p.progress_percent,
            'donor_count': p.donor_count,
            'currency': p.currency,
            'deadline': p.deadline.isoformat() if p.deadline else None,
            'image': request.build_absolute_uri(p.image.url) if p.image else None,
            'is_featured': p.is_featured,
            'country': {'name': p.country.name, 'slug': p.country.slug, 'flag_emoji': p.country.flag_emoji},
            'recent_donors': recent_donors,
        })


class DonationCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        project_id = data.get('project_id')
        if not project_id:
            return Response({'error': 'project_id requis.'}, status=status.HTTP_400_BAD_REQUEST)
        project = get_object_or_404(DonationProject, pk=project_id, is_active=True)

        try:
            amount = float(data.get('amount', 0))
        except (TypeError, ValueError):
            return Response({'error': 'Montant invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({'error': 'Le montant doit être supérieur à 0.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_method = data.get('payment_method', 'bank_transfer')
        currency = data.get('currency', project.currency)
        is_anonymous = bool(data.get('is_anonymous', False))

        donation = DonationModel.objects.create(
            project=project,
            donor_name='' if is_anonymous else data.get('donor_name', ''),
            donor_email='' if is_anonymous else data.get('donor_email', ''),
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            message=data.get('message', ''),
            is_anonymous=is_anonymous,
            status='pending',
        )

        # Bank transfer: stays pending, admin confirms
        if payment_method == 'bank_transfer':
            return Response({
                'donation_id': donation.id,
                'status': 'pending',
                'payment_method': 'bank_transfer',
                'message': 'Votre intention de don a été enregistrée. Veuillez effectuer le virement bancaire avec la référence ci-dessous.',
                'reference': f'DON-{donation.id:06d}',
                'bank_details': {
                    'beneficiary': 'Wallah We Can',
                    'iban': 'TN59 1234 5678 9012 3456 7890',
                    'bic': 'BIATTNTT',
                    'reference': f'DON-{donation.id:06d}',
                },
            }, status=status.HTTP_201_CREATED)

        # Stripe: create Checkout session (redirect flow, same as shop)
        if payment_method == 'stripe':
            try:
                from api.payments import _get_stripe
                from django.conf import settings as django_settings
                _stripe = _get_stripe()
                tnd_to_eur = float(getattr(django_settings, 'TND_TO_EUR_RATE', 0.30))
                if currency == 'EUR':
                    amount_cents = max(int(round(amount * 100)), 1)
                else:
                    amount_cents = max(int(round(amount * tnd_to_eur * 100)), 1)
                origin = request.build_absolute_uri('/').rstrip('/')
                session = _stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': f'Don — {project.title}',
                                'description': f'École : {project.school}' if project.school else project.title,
                            },
                            'unit_amount': amount_cents,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    customer_email=donation.donor_email or None,
                    success_url=f"{origin}/shop/donate/success/?donation_id={donation.id}",
                    cancel_url=f"{origin}/shop/donate/?project={project.id}",
                    metadata={
                        'donation_id': str(donation.id),
                        'project_id': str(project.id),
                    },
                )
                donation.payment_id = session.id
                donation.save(update_fields=['payment_id'])
                return Response({
                    'donation_id': donation.id,
                    'checkout_url': session.url,
                    'payment_method': 'stripe',
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                donation.delete()
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Méthode de paiement invalide.'}, status=status.HTTP_400_BAD_REQUEST)
