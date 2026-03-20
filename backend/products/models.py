"""
Product models for WWC Shop - Wallah We Can E-Commerce Platform

Includes: Products, Categories, Producers, Reviews, and Composable Boxes
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Producer(models.Model):
    """
    Farm producer creating the products.
    These are parents of GreenSchool students who work on farms.
    """
    name = models.CharField(_('Name'), max_length=200)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    bio = models.TextField(_('Biography'), blank=True)
    bio_en = models.TextField(_('Biography (English)'), blank=True)
    bio_ar = models.TextField(_('Biography (Arabic)'), blank=True)
    location = models.CharField(_('Location'), max_length=200)
    photo = models.ImageField(_('Photo'), upload_to='producers/', blank=True, null=True)
    total_products_sold = models.IntegerField(_('Total Products Sold'), default=0)
    total_earnings = models.DecimalField(
        _('Total Earnings'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    member_since = models.DateField(_('Member Since'), auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Producer')
        verbose_name_plural = _('Producers')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductCategory(models.Model):
    """
    Product categories matching UI navigation:
    SOINS, NUTRITION, BIEN-ETRE, MAISON, COFFRETS, CADEAUX D'ENTREPRISE, COMPOSER MA BOX
    """
    name = models.CharField(_('Name'), max_length=100)
    name_en = models.CharField(_('Name (English)'), max_length=100, blank=True)
    name_ar = models.CharField(_('Name (Arabic)'), max_length=100, blank=True)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'), blank=True)
    description_en = models.TextField(_('Description (English)'), blank=True)
    description_ar = models.TextField(_('Description (Arabic)'), blank=True)
    icon = models.CharField(_('Icon'), max_length=50, blank=True, help_text='Emoji or icon class')
    image = models.ImageField(_('Image'), upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('Parent Category')
    )
    order = models.IntegerField(_('Display Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    show_in_menu = models.BooleanField(_('Show in Menu'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def has_children(self):
        return self.children.filter(is_active=True).exists()

    def get_name(self, language='fr'):
        if language == 'en' and self.name_en:
            return self.name_en
        elif language == 'ar' and self.name_ar:
            return self.name_ar
        return self.name


class Product(models.Model):
    """
    Individual product with impact tracking.
    Core model for the e-commerce platform.
    """
    UNIT_TYPE_CHOICES = [
        ('individual', _('Individual Item')),
        ('box', _('Pre-made Box')),
        ('composable', _('Composable Box Item')),
    ]

    # Basic Info
    name = models.CharField(_('Name'), max_length=200)
    name_en = models.CharField(_('Name (English)'), max_length=200, blank=True)
    name_ar = models.CharField(_('Name (Arabic)'), max_length=200, blank=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    sku = models.CharField(_('SKU'), max_length=50, unique=True)
    description = models.TextField(_('Description'))
    description_en = models.TextField(_('Description (English)'), blank=True)
    description_ar = models.TextField(_('Description (Arabic)'), blank=True)
    short_description = models.CharField(_('Short Description'), max_length=300, blank=True)
    ingredients = models.TextField(_('Ingredients'), blank=True, help_text="Ce qu'il y a dans mon produit")
    ingredients_en = models.TextField(_('Ingredients (English)'), blank=True)
    usage = models.TextField(_('Usage Instructions'), blank=True, help_text='Utilisation')
    usage_en = models.TextField(_('Usage Instructions (English)'), blank=True)

    # Categorization
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_('Category')
    )
    producer = models.ForeignKey(
        Producer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_('Producer')
    )
    unit_type = models.CharField(
        _('Unit Type'),
        max_length=20,
        choices=UNIT_TYPE_CHOICES,
        default='individual'
    )

    # Pricing (multi-currency support)
    price_tnd = models.DecimalField(
        _('Price (TND)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    price_eur = models.DecimalField(
        _('Price (EUR)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    compare_at_price_tnd = models.DecimalField(
        _('Compare at Price (TND)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Original price for showing discount'
    )

    # B2B Pricing (wholesale)
    b2b_min_quantity = models.IntegerField(_('B2B Minimum Quantity'), default=10)
    b2b_price_tnd = models.DecimalField(
        _('B2B Price (TND)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    b2b_price_eur = models.DecimalField(
        _('B2B Price (EUR)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Badges / Certifications
    is_natural = models.BooleanField(_('100% Natural'), default=False)
    is_organic = models.BooleanField(_('Organic/Bio'), default=False)
    is_handmade = models.BooleanField(_('Handmade'), default=False)
    is_vegan = models.BooleanField(_('Vegan'), default=False)
    is_cruelty_free = models.BooleanField(_('Cruelty Free'), default=False)

    # Social Impact - Core to WWC mission
    impact_description = models.CharField(
        _('Impact Description'),
        max_length=500,
        help_text='e.g., "6 barres energetiques peuvent etre fournies a des enfants de Sidi Mechreg"'
    )
    impact_description_en = models.CharField(_('Impact Description (English)'), max_length=500, blank=True)
    impact_description_ar = models.CharField(_('Impact Description (Arabic)'), max_length=500, blank=True)
    impact_school = models.CharField(
        _('Impact School'),
        max_length=200,
        help_text='e.g., "Sidi Mechreg"'
    )
    impact_quantity = models.IntegerField(
        _('Impact Quantity'),
        validators=[MinValueValidator(1)],
        help_text='e.g., 6 (number of items provided per purchase)'
    )
    impact_item = models.CharField(
        _('Impact Item'),
        max_length=100,
        help_text='e.g., "barres energetiques"'
    )
    impact_item_en = models.CharField(_('Impact Item (English)'), max_length=100, blank=True)

    # Inventory
    stock_quantity = models.IntegerField(_('Stock Quantity'), default=0)
    track_inventory = models.BooleanField(_('Track Inventory'), default=True)
    low_stock_threshold = models.IntegerField(_('Low Stock Threshold'), default=10)
    allow_backorder = models.BooleanField(_('Allow Backorder'), default=False)

    # Product attributes
    weight = models.DecimalField(
        _('Weight (g)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    dimensions = models.CharField(_('Dimensions'), max_length=100, blank=True)

    # SEO
    meta_title = models.CharField(_('Meta Title'), max_length=200, blank=True)
    meta_description = models.TextField(_('Meta Description'), blank=True)

    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    is_featured = models.BooleanField(_('Featured'), default=False)

    # Ratings (calculated from reviews)
    average_rating = models.DecimalField(
        _('Average Rating'),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(_('Review Count'), default=0)

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_price(self, currency='TND', is_b2b=False, quantity=1):
        """Get price based on currency, customer type, and quantity"""
        if is_b2b and quantity >= self.b2b_min_quantity:
            if currency == 'EUR' and self.b2b_price_eur:
                return self.b2b_price_eur
            elif self.b2b_price_tnd:
                return self.b2b_price_tnd

        if currency == 'EUR' and self.price_eur:
            return self.price_eur
        return self.price_tnd

    def get_name(self, language='fr'):
        if language == 'en' and self.name_en:
            return self.name_en
        elif language == 'ar' and self.name_ar:
            return self.name_ar
        return self.name

    def get_description(self, language='fr'):
        if language == 'en' and self.description_en:
            return self.description_en
        elif language == 'ar' and self.description_ar:
            return self.description_ar
        return self.description

    def get_impact_description(self, language='fr'):
        if language == 'en' and self.impact_description_en:
            return self.impact_description_en
        elif language == 'ar' and self.impact_description_ar:
            return self.impact_description_ar
        return self.impact_description

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder

    @property
    def is_low_stock(self):
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def discount_percentage(self):
        from decimal import Decimal
        try:
            compare = Decimal(str(self.compare_at_price_tnd))
            price = Decimal(str(self.price_tnd))
            if compare and compare > price:
                return int(((compare - price) / compare) * 100)
        except Exception:
            pass
        return 0

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()


class ProductImage(models.Model):
    """Multiple images per product"""
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name=_('Product')
    )
    image = models.ImageField(_('Image'), upload_to='products/')
    alt_text = models.CharField(_('Alt Text'), max_length=200, blank=True)
    is_primary = models.BooleanField(_('Primary Image'), default=False)
    order = models.IntegerField(_('Display Order'), default=0)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class ComposableBox(models.Model):
    """
    Pre-defined box templates for "COMPOSER MA BOX" feature.
    Customers can select items to fill these boxes.
    """
    name = models.CharField(_('Name'), max_length=200)
    name_en = models.CharField(_('Name (English)'), max_length=200, blank=True)
    slug = models.SlugField(_('Slug'), unique=True)
    description = models.TextField(_('Description'))
    description_en = models.TextField(_('Description (English)'), blank=True)
    image = models.ImageField(_('Image'), upload_to='boxes/')
    min_items = models.IntegerField(_('Minimum Items'), default=3)
    max_items = models.IntegerField(_('Maximum Items'), default=10)
    price_tnd = models.DecimalField(
        _('Base Price (TND)'),
        max_digits=10,
        decimal_places=2,
        help_text='Base price for the box (items may add extra cost)'
    )
    price_eur = models.DecimalField(
        _('Base Price (EUR)'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    eligible_products = models.ManyToManyField(
        Product,
        related_name='eligible_for_boxes',
        blank=True,
        verbose_name=_('Eligible Products'),
        help_text='Products that can be added to this box type'
    )
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Composable Box')
        verbose_name_plural = _('Composable Boxes')
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Product reviews - displayed as "784 avis" in UI.
    Includes rating and verification status.
    """
    product = models.ForeignKey(
        Product,
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name=_('Product')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User')
    )
    rating = models.IntegerField(
        _('Rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(_('Title'), max_length=200, blank=True)
    comment = models.TextField(_('Comment'))
    is_verified_purchase = models.BooleanField(_('Verified Purchase'), default=False)
    is_approved = models.BooleanField(_('Approved'), default=True)
    helpful_votes = models.IntegerField(_('Helpful Votes'), default=0)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product rating after saving review
        self.product.update_rating()


# Add method to Product for updating ratings
def update_product_rating(self):
    """Update average rating based on approved reviews"""
    reviews = self.reviews.filter(is_approved=True)
    if reviews.exists():
        avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
        self.average_rating = round(avg, 2)
        self.review_count = reviews.count()
    else:
        self.average_rating = 0
        self.review_count = 0
    self.save(update_fields=['average_rating', 'review_count'])


Product.update_rating = update_product_rating
