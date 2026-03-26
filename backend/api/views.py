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


def _get_request_lang(request):
    """
    Resolve the requested language from (in priority order):
    1. ?lang= query param
    2. Accept-Language header (first tag only)
    Supported values: 'fr', 'en', 'ar'. Defaults to 'fr'.
    """
    supported = {'fr', 'en', 'ar'}
    lang = request.query_params.get('lang', '').strip().lower()[:2]
    if lang in supported:
        return lang
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if accept:
        lang = accept.split(',')[0].split('-')[0].strip().lower()
        if lang in supported:
            return lang
    return 'fr'

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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = _get_request_lang(self.request)
        return ctx

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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = _get_request_lang(self.request)
        return ctx

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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = _get_request_lang(self.request)
        return ctx

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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = _get_request_lang(self.request)
        return ctx


# ============================================
# Cart Views
# ============================================

class CartViewSet(viewsets.ViewSet):
    """ViewSet for shopping cart operations"""
    permission_classes = [AllowAny]
    # Use JWT authentication so Bearer tokens work, but not SessionAuthentication
    # (which enforces CSRF). Cart identity also accepts X-Session-Key header.
    authentication_classes = [JWTAuthentication]

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
    Rates are read from the DB (ShippingRate model); falls back to hardcoded
    defaults if no matching row exists.
    """
    from orders.models import ShippingRate
    DEFAULT_RATE = 20.00
    DEFAULT_THRESHOLD = 75.00
    try:
        sr = ShippingRate.objects.get(country_code=country, is_active=True)
        threshold = float(sr.free_threshold_tnd)
        rate = float(sr.rate_tnd)
    except ShippingRate.DoesNotExist:
        threshold = DEFAULT_THRESHOLD
        rate = DEFAULT_RATE
    except Exception:
        threshold = DEFAULT_THRESHOLD
        rate = DEFAULT_RATE

    if subtotal >= threshold:
        return 0.00
    return rate


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


def _create_order_items(order, cart):
    """Create OrderItem rows from a live cart and update stock."""
    for cart_item in cart.items.select_related('product', 'composable_box'):
        box = cart_item.composable_box
        if box:
            box_price = box.price_eur if cart.currency == 'EUR' and box.price_eur else box.price_tnd
            impact = cart_item.get_impact()
            OrderItem.objects.create(
                order=order,
                product=None,
                producer=None,
                product_name=box.name,
                product_sku=box.slug,
                quantity=cart_item.quantity,
                unit_price=box_price,
                subtotal=cart_item.get_subtotal(cart.currency),
                impact_quantity=impact.get('quantity', 0),
                impact_item=impact.get('item', ''),
                impact_school=impact.get('school', ''),
            )
        else:
            p = cart_item.product
            OrderItem.objects.create(
                order=order,
                product=p,
                producer=p.producer,
                product_name=p.name,
                product_sku=p.sku,
                quantity=cart_item.quantity,
                unit_price=p.get_price(cart.currency),
                subtotal=cart_item.get_subtotal(cart.currency),
                impact_quantity=p.impact_quantity * cart_item.quantity,
                impact_item=p.impact_item,
                impact_school=p.impact_school,
            )
            if p.track_inventory:
                p.stock_quantity -= cart_item.quantity
                p.save(update_fields=['stock_quantity'])


def _create_order_items_from_snapshot(order, snapshot):
    """Create OrderItem rows from a cart snapshot (used after Stripe webhook)."""
    from products.models import Product, Producer
    from decimal import Decimal
    for item in snapshot['items']:
        if item['type'] == 'box':
            OrderItem.objects.create(
                order=order,
                product=None,
                producer=None,
                product_name=item['name'],
                product_sku=item['sku'],
                quantity=item['quantity'],
                unit_price=Decimal(item['unit_price']),
                subtotal=Decimal(item['subtotal']),
                impact_quantity=item['impact_quantity'],
                impact_item=item['impact_item'],
                impact_school=item['impact_school'],
            )
        else:
            product = Product.objects.filter(pk=item['product_id']).first()
            producer = Producer.objects.filter(pk=item['producer_id']).first() if item.get('producer_id') else None
            OrderItem.objects.create(
                order=order,
                product=product,
                producer=producer,
                product_name=item['name'],
                product_sku=item['sku'],
                quantity=item['quantity'],
                unit_price=Decimal(item['unit_price']),
                subtotal=Decimal(item['subtotal']),
                impact_quantity=item['impact_quantity'],
                impact_item=item['impact_item'],
                impact_school=item['impact_school'],
            )
            if item.get('track_inventory') and product:
                product.stock_quantity -= item['quantity']
                product.save(update_fields=['stock_quantity'])


class CheckoutView(APIView):
    """Handle checkout process"""
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.session.session_key:
            request.session.create()

        cart = CartViewSet().get_cart(request)
        if not cart or cart.items.count() == 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        payment_method = data['payment_method']

        # --- Stripe: save intent only, create order after webhook confirms ---
        if payment_method == 'stripe':
            return self._handle_stripe_intent(request, cart, data)

        # --- COD / Bank transfer: create order immediately ---
        return self._create_order_and_respond(request, cart, data)

    def _collect_cart_snapshot(self, cart):
        """Capture cart items as plain dicts for later order creation."""
        snapshot = {'currency': cart.currency, 'items': []}
        for item in cart.items.select_related('product', 'composable_box'):
            box = item.composable_box
            if box:
                impact = item.get_impact()
                box_price = box.price_eur if cart.currency == 'EUR' and box.price_eur else box.price_tnd
                snapshot['items'].append({
                    'type': 'box',
                    'name': box.name,
                    'sku': box.slug,
                    'quantity': item.quantity,
                    'unit_price': str(box_price),
                    'subtotal': str(item.get_subtotal(cart.currency)),
                    'impact_quantity': impact.get('quantity', 0),
                    'impact_item': impact.get('item', ''),
                    'impact_school': impact.get('school', ''),
                    'track_inventory': False,
                })
            else:
                p = item.product
                is_b2b = (
                    cart.user and
                    hasattr(cart.user, 'customer') and
                    cart.user.customer.is_b2b
                )
                snapshot['items'].append({
                    'type': 'product',
                    'product_id': p.id,
                    'producer_id': p.producer_id,
                    'name': p.name,
                    'sku': p.sku,
                    'quantity': item.quantity,
                    'unit_price': str(p.get_price(cart.currency, is_b2b=is_b2b, quantity=item.quantity)),
                    'subtotal': str(item.get_subtotal(cart.currency)),
                    'impact_quantity': p.impact_quantity * item.quantity,
                    'impact_item': p.impact_item,
                    'impact_school': p.impact_school,
                    'track_inventory': p.track_inventory,
                })
        return snapshot

    def _handle_stripe_intent(self, request, cart, data):
        """For Stripe: save a PendingCheckout and return a Stripe session URL.
        The actual Order is created only when the webhook fires."""
        from decimal import Decimal
        from orders.models import PendingCheckout
        import stripe as _stripe_lib
        from django.conf import settings as django_settings

        subtotal = cart.get_total()
        country = data.get('shipping_country', 'TN')
        shipping_cost = Decimal(str(_calculate_shipping(country, float(subtotal), cart.currency)))
        gift_packaging = data.get('gift_packaging', False)
        gift_packaging_fee = Decimal('5.00') if (gift_packaging and cart.currency == 'TND') else (Decimal('2.00') if gift_packaging else Decimal('0.00'))

        coupon_code = data.get('coupon_code', '').strip().upper()
        discount_amount = Decimal('0.00')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                valid, _ = coupon.is_valid(float(subtotal))
                if valid:
                    discount_amount = coupon.calculate_discount(subtotal)
            except Coupon.DoesNotExist:
                pass

        total = subtotal + shipping_cost + gift_packaging_fee - discount_amount

        # Snapshot cart before any clearing
        cart_snapshot = self._collect_cart_snapshot(cart)

        # Serialise form data (convert Decimal to str for JSON)
        serialisable_data = {k: str(v) if hasattr(v, '__round__') else v for k, v in data.items()}

        pending = PendingCheckout.objects.create(
            user=request.user if request.user.is_authenticated else None,
            cart_snapshot=cart_snapshot,
            form_data={
                **serialisable_data,
                '_subtotal': str(subtotal),
                '_shipping_cost': str(shipping_cost),
                '_gift_packaging_fee': str(gift_packaging_fee),
                '_discount_amount': str(discount_amount),
                '_total': str(total),
            },
        )

        # Build Stripe line items
        _stripe_lib.api_key = django_settings.STRIPE_SECRET_KEY
        from orders.models import SiteSettings
        tnd_to_eur = SiteSettings.get_tnd_to_eur()

        def to_cents(amount, currency):
            if currency == 'EUR':
                return max(int(round(float(amount) * 100)), 1)
            return max(int(round(float(amount) * tnd_to_eur * 100)), 1)

        line_items = []
        for item in cart_snapshot['items']:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': item['name']},
                    'unit_amount': to_cents(item['unit_price'], cart_snapshot['currency']),
                },
                'quantity': item['quantity'],
            })

        if float(shipping_cost) > 0:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': 'Livraison'},
                    'unit_amount': to_cents(shipping_cost, cart_snapshot['currency']),
                },
                'quantity': 1,
            })

        origin = request.build_absolute_uri('/').rstrip('/')
        try:
            session = _stripe_lib.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                customer_email=data.get('email'),
                success_url=f"{origin}/shop/order-success/?method=stripe&pending={pending.id}",
                cancel_url=f"{origin}/shop/checkout/?payment=cancelled",
                metadata={'pending_checkout_id': str(pending.id)},
            )
            pending.stripe_session_id = session.id
            pending.save(update_fields=['stripe_session_id'])
        except Exception as e:
            logger.error("Stripe session creation failed for PendingCheckout %s: %s", getattr(pending, 'id', '?'), e)
            try:
                pending.delete()
            except Exception:
                pass
            # Give a friendlier message for network connectivity issues
            err_str = str(e)
            if 'getaddrinfo' in err_str or 'NameResolution' in err_str or 'ConnectionError' in err_str or 'APIConnectionError' in err_str:
                user_msg = 'Impossible de joindre Stripe. Vérifiez la connexion internet du serveur.'
            else:
                user_msg = 'Erreur lors de la création de la session de paiement. Veuillez réessayer.'
            return Response({'error': user_msg}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Clear cart now — items are snapshotted
        cart.clear()

        return Response({
            'checkout_url': session.url,
            'pending_checkout_id': str(pending.id),
            'payment_method': 'stripe',
        }, status=status.HTTP_200_OK)

    def _create_order_and_respond(self, request, cart, data):
        """Create order immediately (COD / bank transfer)."""
        from decimal import Decimal

        subtotal = cart.get_total()
        country = data.get('shipping_country', 'TN')
        shipping_cost = Decimal(str(_calculate_shipping(country, float(subtotal), cart.currency)))
        gift_packaging = data.get('gift_packaging', False)
        gift_packaging_fee = Decimal('5.00') if (gift_packaging and cart.currency == 'TND') else (Decimal('2.00') if gift_packaging else Decimal('0.00'))

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
        impact_summary = cart.get_total_impact()
        total_impact = sum(impact_summary.values())

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
            billing_same_as_shipping=data.get('billing_same_as_shipping', True),
            billing_first_name=data.get('billing_first_name', ''),
            billing_last_name=data.get('billing_last_name', ''),
            billing_company=data.get('billing_company', ''),
            billing_address_1=data.get('billing_address_1', ''),
            billing_address_2=data.get('billing_address_2', ''),
            billing_city=data.get('billing_city', ''),
            billing_postal_code=data.get('billing_postal_code', ''),
            billing_country=data.get('billing_country', ''),
            payment_method=data['payment_method'],
            customer_notes=data.get('customer_notes', ''),
            coupon_code=coupon_code,
        )

        _create_order_items(order, cart)
        cart.clear()

        from .payments import _send_order_confirmation_email
        if order.payment_method == 'cash_on_delivery':
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save(update_fields=['status', 'paid_at'])
            if order.user and hasattr(order.user, 'customer'):
                order.user.customer.update_impact_stats()
            _send_order_confirmation_email(order)
        elif order.payment_method == 'bank_transfer':
            _send_order_confirmation_email(order)

        return Response({
            'order_number': order.order_number,
            'order_id': str(order.id),
            'total': str(order.total),
            'currency': order.currency,
            'status': order.status,
            'payment_method': order.payment_method,
        }, status=status.HTTP_201_CREATED)


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

        # Calculate impact live from confirmed orders (never stale)
        CONFIRMED = ['paid', 'processing', 'shipped', 'delivered']
        confirmed_orders = Order.objects.filter(user=request.user, status__in=CONFIRMED)
        breakdown = {}
        total_items = 0
        total_purchases = sum(o.total for o in confirmed_orders)
        for order in confirmed_orders:
            for item_type, qty in (order.impact_summary or {}).items():
                if qty > 0:
                    breakdown[item_type] = breakdown.get(item_type, 0) + qty
                    total_items += qty
        impact_summary = {
            'total_items': total_items,
            'breakdown': breakdown,
            'total_purchases': str(total_purchases),
            'total_orders': confirmed_orders.count(),
        }

        # Get recent donations
        from donations.models import Donation as DonationModel
        recent_donations = DonationModel.objects.filter(
            user=request.user
        ).select_related('project').order_by('-created_at')[:5]
        donations_data = [{
            'id': d.id,
            'project_title': d.project.title,
            'amount': str(d.amount),
            'currency': d.currency,
            'status': d.status,
            'payment_method': d.payment_method,
            'created_at': d.created_at.isoformat(),
        } for d in recent_donations]

        return Response({
            'customer': CustomerSerializer(customer).data,
            'recent_orders': OrderListSerializer(recent_orders, many=True).data,
            'wishlist': WishlistSerializer(wishlist, many=True).data,
            'impact_summary': impact_summary,
            'recent_donations': donations_data,
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

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['lang'] = _get_request_lang(self.request)
        return ctx


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

        lang = _get_request_lang(request)
        return Response({
            'total_impact_items': total_impact,
            'total_orders': total_orders.count(),
            'recent_events': ImpactEventSerializer(recent_events, many=True, context={'lang': lang}).data,
        })


# ============================================
# Auth Views
# ============================================

def _send_email_verification(request, user):
    """Send email verification link to newly registered user."""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.core.mail import send_mail
    from django.conf import settings

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = f"{settings.SITE_URL}/shop/verify-email/?uid={uid}&token={token}"

    send_mail(
        subject='Confirmez votre adresse email - Wallah We Can',
        message=(
            f"Bonjour {user.first_name or user.email},\n\n"
            f"Merci de vous être inscrit sur Wallah We Can !\n\n"
            f"Cliquez sur ce lien pour confirmer votre adresse email :\n{verify_url}\n\n"
            "Ce lien est valable 24 heures.\n\n"
            "L'équipe WWC"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


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

        # Send email verification
        _send_email_verification(request, user)

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
                'customer_type': user.customer.customer_type if hasattr(user, 'customer') else 'individual',
                'b2b_status': user.customer.b2b_status if hasattr(user, 'customer') else 'not_applicable',
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
                'b2b_status': user.customer.b2b_status if hasattr(user, 'customer') else 'not_applicable',
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

        from django.conf import settings as django_settings

        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Email requis'}, status=status.HTTP_400_BAD_REQUEST)

        # Always return success to avoid email enumeration
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{django_settings.SITE_URL}/shop/reset-password/?uid={uid}&token={token}"

            send_mail(
                subject='Réinitialisation de votre mot de passe - Wallah We Can',
                message=(
                    f"Bonjour {user.first_name},\n\n"
                    f"Cliquez sur ce lien pour réinitialiser votre mot de passe :\n{reset_url}\n\n"
                    "Ce lien est valable 24 heures.\n\n"
                    "Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.\n\n"
                    "L'équipe WWC"
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
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


class ChangePasswordView(APIView):
    """Change password for authenticated user (requires current password)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not all([current_password, new_password, confirm_password]):
            return Response({'error': 'Tous les champs sont requis'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(current_password):
            return Response({'error': 'Mot de passe actuel incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Les mots de passe ne correspondent pas'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({'error': 'Le mot de passe doit contenir au moins 8 caractères'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': 'Mot de passe modifié avec succès'})


class EmailVerificationView(APIView):
    """Verify email address using uid + token from verification email."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from django.contrib.auth.models import User
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        uid = request.query_params.get('uid', '')
        token = request.query_params.get('token', '')

        if not uid or not token:
            return Response({'error': 'Lien invalide'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Lien invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Lien expiré ou invalide'}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(user, 'customer'):
            user.customer.email_verified = True
            user.customer.save(update_fields=['email_verified'])

        return Response({'message': 'Email confirmé avec succès'})

    def post(self, request):
        """Resend verification email (requires authentication)."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentification requise'}, status=status.HTTP_401_UNAUTHORIZED)

        _send_email_verification(request, request.user)
        return Response({'message': 'Email de vérification envoyé'})


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
            'image': request.build_absolute_uri(c.image.url) if c.image else None,
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
    authentication_classes = [JWTAuthentication, CsrfExemptSessionAuthentication]

    def post(self, request):
        data = request.data
        project_id = data.get('project_id') or data.get('project')
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

        # Auto-fill from authenticated user if logged in
        linked_user = request.user if request.user.is_authenticated else None
        if linked_user and not is_anonymous:
            auto_name = f"{linked_user.first_name} {linked_user.last_name}".strip() or linked_user.username
            auto_email = linked_user.email
        else:
            auto_name = data.get('donor_name', '')
            auto_email = data.get('donor_email', '')

        donation = DonationModel.objects.create(
            project=project,
            user=linked_user,
            donor_name='' if is_anonymous else auto_name,
            donor_email='' if is_anonymous else auto_email,
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
                from orders.models import SiteSettings
                _stripe = _get_stripe()
                tnd_to_eur = SiteSettings.get_tnd_to_eur()
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


class ShippingRateListView(APIView):
    """
    Public read-only endpoint that returns active shipping rates.
    Used by the checkout page to display shipping costs per country and by
    the WordPress plugin to calculate shipping dynamically.

    GET /api/v1/shipping-rates/
    GET /api/v1/shipping-rates/?country_code=TN
    GET /api/v1/shipping-rates/?is_active=true
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        from orders.models import ShippingRate
        qs = ShippingRate.objects.all()

        country_code = request.query_params.get('country_code')
        if country_code:
            qs = qs.filter(country_code__iexact=country_code.strip())

        is_active_param = request.query_params.get('is_active')
        if is_active_param is not None:
            qs = qs.filter(is_active=(is_active_param.lower() not in ('false', '0', 'no')))

        rates = [
            {
                'id': r.id,
                'country_code': r.country_code,
                'country_name': r.country_name,
                'rate_tnd': str(r.rate_tnd),
                'free_threshold_tnd': str(r.free_threshold_tnd),
                'is_active': r.is_active,
                'updated_at': r.updated_at.isoformat(),
            }
            for r in qs.order_by('country_name')
        ]
        return Response({'count': len(rates), 'results': rates})
