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
from django.db.models import Q
from django.shortcuts import get_object_or_404

from products.models import Product, ProductImage, ProductCategory, Producer
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


class AdminCategoryManageViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for categories management.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminCategoryManageSerializer
    queryset = ProductCategory.objects.all().order_by('order', 'name')
    lookup_field = 'id'


class AdminProducerListView(generics.ListAPIView):
    """
    List all producers for dropdown selection in product editor.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminProducerListSerializer
    queryset = Producer.objects.filter(is_active=True).order_by('name')


class AdminProducerManageViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for producers management.
    """
    authentication_classes = [AdminAPIKeyAuthentication]
    permission_classes = [IsAdminAPIKeyAuthenticated]
    serializer_class = AdminProducerManageSerializer
    queryset = Producer.objects.all().order_by('name')
    lookup_field = 'id'


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

        return Response({
            'total_products': total_products,
            'published_products': published_products,
            'draft_products': draft_products,
            'low_stock_products': low_stock,
            'missing_english': missing_en,
            'missing_arabic': missing_ar,
            'categories_count': ProductCategory.objects.filter(is_active=True).count(),
            'producers_count': Producer.objects.filter(is_active=True).count(),
        })
