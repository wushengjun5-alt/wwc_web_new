"""
Admin Views for WWC Shop Product Management

These views provide CRUD endpoints for the WordPress admin interface.
Protected by API key authentication.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from products.models import Product, ProductImage, ProductCategory, Producer
from orders.models import Order, Coupon, ImpactEvent
from customers.models import Customer
from donations.models import Country, DonationProject, Donation as DonationModel
from .admin_serializers import (
    AdminProductListSerializer,
    AdminProductDetailSerializer,
    AdminProductCreateUpdateSerializer,
    AdminProductImageSerializer,
    AdminProductImageUploadSerializer,
    AdminCategoryListSerializer,
    AdminCategoryManageSerializer,
    AdminProducerListSerializer,
    AdminProducerManageSerializer,
    AdminBulkActionSerializer,
)
from .admin_auth import AdminAPIKeyAuthentication, IsAdminAPIKeyAuthenticated


class AdminProductViewSet(viewsets.ModelViewSet):
    """
    Admin ViewSet for Product CRUD operations.

    Endpoints:
    - GET /api/admin/products/ - List products with filtering
    - POST /api/admin/products/ - Create product
    - GET /api/admin/products/{id}/ - Get product details
    - PATCH /api/admin/products/{id}/ - Update product
    - DELETE /api/admin/products/{id}/ - Delete product
    - POST /api/admin/products/{id}/images/ - Upload image
    - DELETE /api/admin/products/{id}/images/{image_id}/ - Delete image
    - POST /api/admin/products/bulk/ - Bulk actions
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    lookup_field = 'id'

    def get_queryset(self):
        """
        Return products with optional filtering.
        Includes drafts (is_active=False) for admin.
        """
        queryset = Product.objects.all().select_related('category', 'producer')

        # Search filter
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(name_en__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )

        # Status filter (published/draft)
        status_filter = self.request.query_params.get('status', '')
        if status_filter == 'published':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'draft':
            queryset = queryset.filter(is_active=False)

        # Category filter
        category = self.request.query_params.get('category', '')
        if category:
            try:
                queryset = queryset.filter(category_id=int(category))
            except ValueError:
                queryset = queryset.filter(category__slug=category)

        # Language completeness filter
        lang_complete = self.request.query_params.get('lang_complete', '')
        if lang_complete == 'en':
            queryset = queryset.exclude(
                Q(name_en__isnull=True) | Q(name_en='') |
                Q(description_en__isnull=True) | Q(description_en='')
            )
        elif lang_complete == 'ar':
            queryset = queryset.exclude(
                Q(name_ar__isnull=True) | Q(name_ar='') |
                Q(description_ar__isnull=True) | Q(description_ar='')
            )
        elif lang_complete == 'incomplete':
            # Products missing any translation
            queryset = queryset.filter(
                Q(name_en__isnull=True) | Q(name_en='') |
                Q(name_ar__isnull=True) | Q(name_ar='')
            )

        # Featured filter
        is_featured = self.request.query_params.get('is_featured', '')
        if is_featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)

        # Low stock filter
        low_stock = self.request.query_params.get('low_stock', '')
        if low_stock.lower() == 'true':
            queryset = queryset.filter(track_inventory=True, stock_quantity__lte=10)

        # Out of stock filter
        out_of_stock = self.request.query_params.get('out_of_stock', '')
        if out_of_stock.lower() == 'true':
            queryset = queryset.filter(stock_quantity=0)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-updated_at')
        valid_orderings = ['name', '-name', 'price_tnd', '-price_tnd',
                          'created_at', '-created_at', 'updated_at', '-updated_at',
                          'stock_quantity', '-stock_quantity']
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-updated_at')

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return AdminProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AdminProductCreateUpdateSerializer
        return AdminProductDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new product"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Return detailed response
        detail_serializer = AdminProductDetailSerializer(
            product, context={'request': request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Get a single product with better error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            import traceback
            return Response({
                'error': str(e),
                'detail': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Update a product (full or partial)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Return detailed response
        detail_serializer = AdminProductDetailSerializer(
            product, context={'request': request}
        )
        return Response(detail_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a product"""
        instance = self.get_object()
        product_name = instance.name
        instance.delete()
        return Response({
            'message': f'Produit "{product_name}" supprimé avec succès.',
            'deleted': True
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='images')
    def upload_image(self, request, id=None):
        """Upload an image to a product"""
        product = self.get_object()
        serializer = AdminProductImageUploadSerializer(
            data=request.data,
            context={'product': product, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        image = serializer.save()

        return Response(
            AdminProductImageSerializer(image, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, id=None, image_id=None):
        """Delete an image from a product"""
        product = self.get_object()
        image = get_object_or_404(ProductImage, id=image_id, product=product)
        was_primary = image.is_primary
        image.delete()

        # If we deleted the primary image, make the first remaining image primary
        if was_primary:
            first_image = product.images.first()
            if first_image:
                first_image.is_primary = True
                first_image.save()

        return Response({
            'message': 'Image supprimée avec succès.',
            'deleted': True
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='images/(?P<image_id>[^/.]+)/primary')
    def set_primary_image(self, request, id=None, image_id=None):
        """Set an image as the primary image"""
        product = self.get_object()
        image = get_object_or_404(ProductImage, id=image_id, product=product)

        # Unmark all other images
        ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)

        # Mark this one as primary
        image.is_primary = True
        image.save()

        return Response({
            'message': 'Image définie comme image principale.',
            'image': AdminProductImageSerializer(image, context={'request': request}).data
        })

    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk_action(self, request):
        """Perform bulk actions on products"""
        serializer = AdminBulkActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']
        product_ids = serializer.validated_data['product_ids']

        products = Product.objects.filter(id__in=product_ids)
        count = products.count()

        if action_type == 'publish':
            products.update(is_active=True)
            message = f'{count} produit(s) publié(s) avec succès.'
        elif action_type == 'unpublish':
            products.update(is_active=False)
            message = f'{count} produit(s) mis en brouillon.'
        elif action_type == 'delete':
            products.delete()
            message = f'{count} produit(s) supprimé(s).'
        else:
            return Response(
                {'error': 'Action non reconnue.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'message': message,
            'affected_count': count
        })

    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate(self, request, id=None):
        """Duplicate a product as a draft"""
        original = self.get_object()

        # Create a copy
        new_product = Product.objects.get(pk=original.pk)
        new_product.pk = None
        new_product.slug = f"{original.slug}-copy"
        new_product.sku = f"{original.sku}-COPY"
        new_product.name = f"{original.name} (Copie)"
        new_product.is_active = False  # Always start as draft
        new_product.average_rating = 0
        new_product.review_count = 0

        # Ensure unique slug
        counter = 1
        base_slug = new_product.slug
        while Product.objects.filter(slug=new_product.slug).exists():
            new_product.slug = f"{base_slug}-{counter}"
            counter += 1

        # Ensure unique SKU
        counter = 1
        base_sku = new_product.sku
        while Product.objects.filter(sku=new_product.sku).exists():
            new_product.sku = f"{base_sku}-{counter}"
            counter += 1

        new_product.save()

        # Copy images
        for image in original.images.all():
            ProductImage.objects.create(
                product=new_product,
                image=image.image,
                alt_text=image.alt_text,
                is_primary=image.is_primary,
                order=image.order
            )

        detail_serializer = AdminProductDetailSerializer(
            new_product, context={'request': request}
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class AdminCategoryListView(generics.ListAPIView):
    """
    List all categories for dropdown selection in product editor.
    Returns categories in a flat list with parent info.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminCategoryListSerializer
    queryset = ProductCategory.objects.filter(is_active=True).order_by('order', 'name')
    pagination_class = None  # Disable pagination for dropdown lists


class AdminCategoryManageViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for categories management.
    Deleting a category will also delete all products in that category.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminCategoryManageSerializer
    queryset = ProductCategory.objects.all().order_by('order', 'name')
    lookup_field = 'id'
    pagination_class = None  # Disable pagination for admin management

    def destroy(self, request, *args, **kwargs):
        """Delete category and all associated products"""
        instance = self.get_object()
        category_name = instance.name
        products_count = instance.products.count()

        # Delete all products in this category
        instance.products.all().delete()

        # Delete the category
        instance.delete()

        return Response({
            'message': f'Catégorie "{category_name}" supprimée avec {products_count} produit(s).',
            'deleted': True,
            'products_deleted': products_count
        }, status=status.HTTP_200_OK)


class AdminProducerListView(generics.ListAPIView):
    """
    List all producers for dropdown selection in product editor.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminProducerListSerializer
    queryset = Producer.objects.filter(is_active=True).order_by('name')
    pagination_class = None  # Disable pagination for dropdown lists


class AdminProducerManageViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for producers management.
    Deleting a producer will also delete all products from that producer.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminProducerManageSerializer
    queryset = Producer.objects.all().order_by('name')
    lookup_field = 'id'
    pagination_class = None  # Disable pagination for admin management

    def destroy(self, request, *args, **kwargs):
        """Delete producer and all associated products"""
        instance = self.get_object()
        producer_name = instance.name
        products_count = instance.products.count()

        # Delete all products from this producer
        instance.products.all().delete()

        # Delete the producer
        instance.delete()

        return Response({
            'message': f'Producteur "{producer_name}" supprimé avec {products_count} produit(s).',
            'deleted': True,
            'products_deleted': products_count
        }, status=status.HTTP_200_OK)


class AdminStatsView(APIView):
    """
    Get admin dashboard statistics.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        total_products = Product.objects.count()
        published_products = Product.objects.filter(is_active=True).count()
        draft_products = Product.objects.filter(is_active=False).count()
        low_stock = Product.objects.filter(
            track_inventory=True,
            stock_quantity__lte=10
        ).count()

        # Language completeness
        missing_en = Product.objects.filter(
            Q(name_en__isnull=True) | Q(name_en='')
        ).count()
        missing_ar = Product.objects.filter(
            Q(name_ar__isnull=True) | Q(name_ar='')
        ).count()

        # Order stats
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        total_revenue = Order.objects.filter(
            status__in=['paid', 'processing', 'shipped', 'delivered']
        ).aggregate(rev=Sum('total'))['rev'] or 0

        return Response({
            'total_products': total_products,
            'published_products': published_products,
            'draft_products': draft_products,
            'low_stock_products': low_stock,
            'missing_english': missing_en,
            'missing_arabic': missing_ar,
            'categories_count': ProductCategory.objects.filter(is_active=True).count(),
            'producers_count': Producer.objects.filter(is_active=True).count(),
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': str(total_revenue),
            'total_customers': Customer.objects.count(),
            'active_coupons': Coupon.objects.filter(is_active=True).count(),
            'total_coupons': Coupon.objects.count(),
            'total_impact_events': ImpactEvent.objects.count(),
            'published_impact_events': ImpactEvent.objects.filter(is_published=True).count(),
            'total_items_delivered': ImpactEvent.objects.aggregate(t=Sum('items_delivered'))['t'] or 0,
            'total_donations': DonationModel.objects.filter(status='completed').count(),
            'total_raised': str(DonationModel.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0),
            'pending_donations': DonationModel.objects.filter(status='pending', payment_method='bank_transfer').count(),
        })


# ============================================
# Admin Order Management
# ============================================

class AdminOrderListView(APIView):
    """
    List and filter orders for admin management.
    GET /api/v1/admin/orders/
    Query params: status, search, page, page_size
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        queryset = Order.objects.select_related('user').order_by('-created_at')

        # Filter by status
        status_filter = request.query_params.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search by order number, email, phone
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )

        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        total = queryset.count()
        offset = (page - 1) * page_size
        orders = queryset[offset:offset + page_size]

        data = [{
            'order_number': o.order_number,
            'email': o.email,
            'phone': o.phone,
            'status': o.status,
            'currency': o.currency,
            'total': str(o.total),
            'payment_method': o.payment_method,
            'tracking_number': o.tracking_number or '',
            'created_at': o.created_at.isoformat(),
            'item_count': o.items.count(),
        } for o in orders]

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': data,
        })


class AdminOrderDetailView(APIView):
    """
    Get full order detail or update status/tracking for a single order.
    GET  /api/v1/admin/orders/<order_number>/
    PATCH /api/v1/admin/orders/<order_number>/
      Body: { status, tracking_number }
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    VALID_STATUSES = {'pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'}

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        items = [{
            'product_name': item.product_name,
            'quantity': item.quantity,
            'unit_price': str(item.unit_price),
            'subtotal': str(item.subtotal),
            'impact_quantity': item.impact_quantity,
            'impact_item': item.impact_item or '',
            'impact_school': item.impact_school or '',
        } for item in order.items.all()]

        return Response({
            'order_number': order.order_number,
            'email': order.email,
            'phone': order.phone,
            'status': order.status,
            'currency': order.currency,
            'subtotal': str(order.subtotal),
            'discount_amount': str(order.discount_amount),
            'coupon_code': order.coupon_code or '',
            'shipping_cost': str(order.shipping_cost),
            'tax_amount': str(order.tax_amount),
            'total': str(order.total),
            'payment_method': order.payment_method,
            'tracking_number': order.tracking_number or '',
            'customer_notes': order.customer_notes or '',
            'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
            'paid_at': order.paid_at.isoformat() if order.paid_at else None,
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'items': items,
            'shipping_first_name': order.shipping_first_name,
            'shipping_last_name': order.shipping_last_name,
            'shipping_company': order.shipping_company or '',
            'shipping_address_1': order.shipping_address_1,
            'shipping_address_2': order.shipping_address_2 or '',
            'shipping_city': order.shipping_city,
            'shipping_state': order.shipping_state or '',
            'shipping_postal_code': order.shipping_postal_code,
            'shipping_country': order.shipping_country,
            'total_impact_items': order.total_impact_items,
            'impact_summary': order.impact_summary,
        })

    def patch(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        updated_fields = []
        send_shipping_email = False

        new_status = request.data.get('status')
        if new_status is not None:
            if new_status not in self.VALID_STATUSES:
                return Response(
                    {'error': f'Statut invalide. Valeurs acceptées : {", ".join(sorted(self.VALID_STATUSES))}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            order.status = new_status
            updated_fields.append('status')

            # Auto-set shipped_at / delivered_at timestamps
            if new_status == 'shipped' and not order.shipped_at:
                order.shipped_at = timezone.now()
                updated_fields.append('shipped_at')
                send_shipping_email = True
            elif new_status == 'delivered' and not order.delivered_at:
                order.delivered_at = timezone.now()
                updated_fields.append('delivered_at')

        tracking = request.data.get('tracking_number')
        if tracking is not None:
            order.tracking_number = tracking.strip()
            updated_fields.append('tracking_number')

        if not updated_fields:
            return Response({'error': 'Aucun champ à mettre à jour.'}, status=status.HTTP_400_BAD_REQUEST)

        order.save(update_fields=updated_fields)

        # Send shipping notification email after save
        if send_shipping_email:
            try:
                from .payments import _send_shipping_confirmation_email
                _send_shipping_confirmation_email(order)
            except Exception:
                pass  # Non-blocking — email failure should not fail the API response

        return Response({
            'order_number': order.order_number,
            'status': order.status,
            'tracking_number': order.tracking_number or '',
            'updated_fields': updated_fields,
            'message': 'Commande mise à jour avec succès.',
        })


# ============================================
# Admin Customer Management
# ============================================

class AdminCustomerListView(APIView):
    """
    List customers for admin.
    GET /api/v1/admin/customers/
    Query params: search, page, page_size
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        queryset = Customer.objects.select_related('user').order_by('-user__date_joined')

        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(phone__icontains=search)
            )

        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        total = queryset.count()
        offset = (page - 1) * page_size
        customers = queryset[offset:offset + page_size]

        data = [{
            'id': c.id,
            'email': c.user.email,
            'first_name': c.user.first_name,
            'last_name': c.user.last_name,
            'phone': c.phone or '',
            'customer_type': c.customer_type,
            'total_orders': c.total_orders,
            'total_purchases': str(c.total_purchases),
            'total_impact_items': c.total_impact_items,
            'date_joined': c.user.date_joined.isoformat(),
            'is_active': c.user.is_active,
        } for c in customers]

        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'results': data,
        })


# ============================================
# Admin Coupon Management
# ============================================

class AdminCouponListView(APIView):
    """
    List and create coupons.
    GET  /api/v1/admin/coupons/
    POST /api/v1/admin/coupons/
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        queryset = Coupon.objects.all().order_by('-created_at')

        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(code__icontains=search)

        is_active = request.query_params.get('is_active', '')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)

        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        total = queryset.count()
        offset = (page - 1) * page_size
        coupons = queryset[offset:offset + page_size]

        data = [{
            'id': c.id,
            'code': c.code,
            'discount_type': c.discount_type,
            'discount_value': str(c.discount_value),
            'min_order_amount': str(c.min_order_amount),
            'max_uses': c.max_uses,
            'used_count': c.used_count,
            'is_active': c.is_active,
            'valid_from': c.valid_from.isoformat() if c.valid_from else None,
            'valid_until': c.valid_until.isoformat() if c.valid_until else None,
            'created_at': c.created_at.isoformat(),
        } for c in coupons]

        return Response({'count': total, 'page': page, 'page_size': page_size, 'results': data})

    def post(self, request):
        data = request.data
        try:
            coupon = Coupon.objects.create(
                code=data['code'].strip().upper(),
                discount_type=data.get('discount_type', 'percent'),
                discount_value=data['discount_value'],
                min_order_amount=data.get('min_order_amount', 0),
                max_uses=data.get('max_uses', 0),
                is_active=data.get('is_active', True),
                valid_from=data.get('valid_from') or None,
                valid_until=data.get('valid_until') or None,
            )
            return Response({'id': coupon.id, 'code': coupon.code, 'message': 'Coupon créé avec succès.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminCouponDetailView(APIView):
    """
    Retrieve, update, or delete a coupon.
    GET    /api/v1/admin/coupons/<id>/
    PATCH  /api/v1/admin/coupons/<id>/
    DELETE /api/v1/admin/coupons/<id>/
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def _get_coupon(self, pk):
        return get_object_or_404(Coupon, pk=pk)

    def get(self, request, pk):
        c = self._get_coupon(pk)
        return Response({
            'id': c.id,
            'code': c.code,
            'discount_type': c.discount_type,
            'discount_value': str(c.discount_value),
            'min_order_amount': str(c.min_order_amount),
            'max_uses': c.max_uses,
            'used_count': c.used_count,
            'is_active': c.is_active,
            'valid_from': c.valid_from.isoformat() if c.valid_from else None,
            'valid_until': c.valid_until.isoformat() if c.valid_until else None,
            'created_at': c.created_at.isoformat(),
        })

    def patch(self, request, pk):
        c = self._get_coupon(pk)
        data = request.data
        updatable = ['discount_type', 'discount_value', 'min_order_amount', 'max_uses', 'is_active', 'valid_from', 'valid_until']
        for field in updatable:
            if field in data:
                val = data[field]
                if field in ('valid_from', 'valid_until') and val == '':
                    val = None
                setattr(c, field, val)
        if 'code' in data:
            c.code = data['code'].strip().upper()
        try:
            c.save()
            return Response({'message': 'Coupon mis à jour.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        c = self._get_coupon(pk)
        c.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================
# Admin Impact Event Management
# ============================================

class AdminImpactEventListView(APIView):
    """
    List and create impact events.
    GET  /api/v1/admin/impact-events/
    POST /api/v1/admin/impact-events/
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        queryset = ImpactEvent.objects.all().order_by('-date')

        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(school__icontains=search)
            )

        is_published = request.query_params.get('is_published', '')
        if is_published == 'true':
            queryset = queryset.filter(is_published=True)
        elif is_published == 'false':
            queryset = queryset.filter(is_published=False)

        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        total = queryset.count()
        offset = (page - 1) * page_size
        events = queryset[offset:offset + page_size]

        data = [{
            'id': e.id,
            'title': e.title,
            'title_en': e.title_en or '',
            'school': e.school,
            'date': e.date.isoformat(),
            'items_delivered': e.items_delivered,
            'item_type': e.item_type,
            'is_published': e.is_published,
            'description': e.description,
            'video_url': e.video_url or '',
            'created_at': e.created_at.isoformat(),
        } for e in events]

        return Response({'count': total, 'page': page, 'page_size': page_size, 'results': data})

    def post(self, request):
        data = request.data
        try:
            event = ImpactEvent.objects.create(
                title=data['title'],
                title_en=data.get('title_en', ''),
                description=data.get('description', ''),
                description_en=data.get('description_en', ''),
                school=data['school'],
                date=data['date'],
                items_delivered=data['items_delivered'],
                item_type=data['item_type'],
                video_url=data.get('video_url', '') or '',
                is_published=data.get('is_published', False),
            )
            return Response({'id': event.id, 'title': event.title, 'message': 'Événement créé avec succès.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminImpactEventDetailView(APIView):
    """
    Retrieve, update, or delete an impact event.
    GET    /api/v1/admin/impact-events/<id>/
    PATCH  /api/v1/admin/impact-events/<id>/
    DELETE /api/v1/admin/impact-events/<id>/
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def _get_event(self, pk):
        return get_object_or_404(ImpactEvent, pk=pk)

    def get(self, request, pk):
        e = self._get_event(pk)
        return Response({
            'id': e.id,
            'title': e.title,
            'title_en': e.title_en or '',
            'description': e.description,
            'description_en': e.description_en or '',
            'school': e.school,
            'date': e.date.isoformat(),
            'items_delivered': e.items_delivered,
            'item_type': e.item_type,
            'video_url': e.video_url or '',
            'is_published': e.is_published,
            'created_at': e.created_at.isoformat(),
        })

    def patch(self, request, pk):
        e = self._get_event(pk)
        data = request.data
        updatable = ['title', 'title_en', 'description', 'description_en', 'school', 'date', 'items_delivered', 'item_type', 'video_url', 'is_published']
        for field in updatable:
            if field in data:
                setattr(e, field, data[field])
        try:
            e.save()
            return Response({'message': 'Événement mis à jour.'})
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        e = self._get_event(pk)
        e.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================
# Admin Donation Management
# ============================================


class AdminDonationCountryListView(APIView):
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        countries = Country.objects.all().order_by('order', 'name')
        data = [{
            'id': c.id, 'name': c.name, 'name_en': c.name_en, 'slug': c.slug,
            'flag_emoji': c.flag_emoji, 'description': c.description,
            'is_active': c.is_active, 'order': c.order,
            'project_count': c.projects.count(),
        } for c in countries]
        return Response(data)

    def post(self, request):
        d = request.data
        try:
            c = Country.objects.create(
                name=d['name'], name_en=d.get('name_en', ''), name_ar=d.get('name_ar', ''),
                slug=d['slug'], flag_emoji=d.get('flag_emoji', '🌍'),
                description=d.get('description', ''), is_active=d.get('is_active', True),
                order=d.get('order', 0),
            )
            return Response({'id': c.id, 'name': c.name}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminDonationCountryDetailView(APIView):
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def patch(self, request, pk):
        c = get_object_or_404(Country, pk=pk)
        for field in ['name', 'name_en', 'name_ar', 'slug', 'flag_emoji', 'description', 'is_active', 'order']:
            if field in request.data:
                setattr(c, field, request.data[field])
        try:
            c.save()
            return Response({'message': 'Pays mis à jour.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        get_object_or_404(Country, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminDonationProjectListView(APIView):
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        queryset = DonationProject.objects.all().select_related('country').order_by('-created_at')
        country_id = request.query_params.get('country_id', '')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        is_active = request.query_params.get('is_active', '')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)

        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        total = queryset.count()
        items = queryset[(page-1)*page_size : page*page_size]

        data = [{
            'id': p.id, 'title': p.title, 'title_en': p.title_en,
            'country': {'id': p.country.id, 'name': p.country.name, 'flag_emoji': p.country.flag_emoji},
            'category': p.category, 'school': p.school,
            'goal_amount': str(p.goal_amount), 'raised_amount': str(p.raised_amount),
            'progress_percent': p.progress_percent, 'donor_count': p.donor_count,
            'currency': p.currency, 'deadline': p.deadline.isoformat() if p.deadline else None,
            'is_active': p.is_active, 'is_featured': p.is_featured,
            'created_at': p.created_at.isoformat(),
        } for p in items]
        return Response({'count': total, 'page': page, 'page_size': page_size, 'results': data})

    def post(self, request):
        d = request.data
        try:
            p = DonationProject.objects.create(
                country_id=d['country_id'], title=d['title'], title_en=d.get('title_en', ''),
                description=d.get('description', ''), description_en=d.get('description_en', ''),
                school=d.get('school', ''), category=d.get('category', 'other'),
                goal_amount=d['goal_amount'], currency=d.get('currency', 'TND'),
                deadline=d.get('deadline') or None,
                is_active=d.get('is_active', True), is_featured=d.get('is_featured', False),
            )
            return Response({'id': p.id, 'title': p.title}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminDonationProjectDetailView(APIView):
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request, pk):
        p = get_object_or_404(DonationProject, pk=pk)
        return Response({
            'id': p.id, 'title': p.title, 'title_en': p.title_en,
            'description': p.description, 'description_en': p.description_en,
            'country_id': p.country_id, 'school': p.school, 'category': p.category,
            'goal_amount': str(p.goal_amount), 'raised_amount': str(p.raised_amount),
            'progress_percent': p.progress_percent, 'donor_count': p.donor_count,
            'currency': p.currency, 'deadline': p.deadline.isoformat() if p.deadline else None,
            'is_active': p.is_active, 'is_featured': p.is_featured,
        })

    def patch(self, request, pk):
        p = get_object_or_404(DonationProject, pk=pk)
        for field in ['title', 'title_en', 'description', 'description_en', 'school', 'category',
                      'goal_amount', 'currency', 'is_active', 'is_featured']:
            if field in request.data:
                setattr(p, field, request.data[field])
        if 'country_id' in request.data:
            p.country_id = request.data['country_id']
        if 'deadline' in request.data:
            p.deadline = request.data['deadline'] or None
        try:
            p.save()
            return Response({'message': 'Projet mis à jour.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        get_object_or_404(DonationProject, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminDonationListView(APIView):
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def get(self, request):
        queryset = DonationModel.objects.all().select_related('project').order_by('-created_at')
        project_id = request.query_params.get('project_id', '')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        status_filter = request.query_params.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        total = queryset.count()
        items = queryset[(page-1)*page_size : page*page_size]

        data = [{
            'id': d.id,
            'donor_name': 'Anonyme' if d.is_anonymous else d.donor_name,
            'donor_email': '' if d.is_anonymous else d.donor_email,
            'amount': str(d.amount), 'currency': d.currency,
            'payment_method': d.payment_method, 'status': d.status,
            'message': d.message, 'is_anonymous': d.is_anonymous,
            'project': {'id': d.project.id, 'title': d.project.title},
            'reference': f'DON-{d.id:06d}',
            'created_at': d.created_at.isoformat(),
        } for d in items]
        return Response({'count': total, 'page': page, 'page_size': page_size, 'results': data})


class AdminDonationDetailView(APIView):
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]

    def patch(self, request, pk):
        d = get_object_or_404(DonationModel, pk=pk)
        if 'status' in request.data:
            d.status = request.data['status']
        try:
            d.save()
            return Response({'message': 'Don mis à jour.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
