"""
Order models for WWC Shop - Wallah We Can E-Commerce Platform

Includes: Cart, CartItem, Order, OrderItem, and ImpactEvent
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from products.models import Product, Producer, ComposableBox


class Cart(models.Model):
    """
    Shopping cart for logged-in and guest users.
    Supports both session-based and user-based carts.
    """
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('User')
    )
    session_key = models.CharField(
        _('Session Key'),
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    currency = models.CharField(_('Currency'), max_length=3, default='TND')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart ({self.session_key[:8]}...)"

    def get_total(self, currency=None):
        """Calculate total cart value"""
        currency = currency or self.currency
        total = sum(item.get_subtotal(currency) for item in self.items.all())
        return total

    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    def get_total_impact(self):
        """Calculate total impact from all cart items"""
        total_impact = {}
        for item in self.items.all():
            if not item.product:
                # Composable box item — count number of selected products
                impact_qty = len(item.box_items) * item.quantity
                total_impact['produits artisanaux'] = total_impact.get('produits artisanaux', 0) + impact_qty
                continue
            impact_item = item.product.impact_item
            impact_qty = item.product.impact_quantity * item.quantity
            total_impact[impact_item] = total_impact.get(impact_item, 0) + impact_qty
        return total_impact

    def merge_with(self, other_cart):
        """Merge another cart into this one (used when guest logs in)"""
        for item in other_cart.items.all():
            if item.composable_box:
                existing_item = self.items.filter(composable_box=item.composable_box).first()
            else:
                existing_item = self.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = self
                item.save()
        other_cart.delete()

    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in cart"""
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('Cart')
    )
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_('Product')
    )
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)

    # For composable boxes
    composable_box = models.ForeignKey(
        ComposableBox,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Composable Box')
    )
    box_items = models.JSONField(
        _('Box Items'),
        default=list,
        blank=True,
        help_text='List of product IDs in composable box'
    )

    added_at = models.DateTimeField(_('Added At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ['cart', 'product', 'composable_box']

    def __str__(self):
        if self.composable_box:
            return f"Box: {self.composable_box.name}"
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self, currency='TND'):
        """Calculate subtotal for this item"""
        if self.composable_box:
            # Composable box: flat box price
            if currency == 'EUR' and self.composable_box.price_eur:
                return self.composable_box.price_eur * self.quantity
            return self.composable_box.price_tnd * self.quantity
        is_b2b = (
            self.cart.user and
            hasattr(self.cart.user, 'customer') and
            self.cart.user.customer.customer_type == 'company'
        )
        price = self.product.get_price(currency, is_b2b, self.quantity)
        return price * self.quantity

    def get_impact(self):
        """Get impact for this cart item"""
        if self.composable_box:
            return {
                'item': 'produits artisanaux',
                'quantity': len(self.box_items) * self.quantity,
                'school': 'GreenSchool',
            }
        return {
            'item': self.product.impact_item,
            'quantity': self.product.impact_quantity * self.quantity,
            'school': self.product.impact_school,
        }


class Order(models.Model):
    """Customer orders with full tracking"""
    STATUS_CHOICES = [
        ('pending', _('Pending Payment')),
        ('paid', _('Paid')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('stripe', _('Stripe (Card)')),
        ('bank_transfer', _('Bank Transfer')),
        ('cash_on_delivery', _('Cash on Delivery')),
    ]

    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(_('Order Number'), max_length=50, unique=True, db_index=True)

    # Customer info
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name=_('User')
    )
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Phone'), max_length=20)

    # Order status
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    currency = models.CharField(_('Currency'), max_length=3, default='TND')

    # Amounts
    subtotal = models.DecimalField(_('Subtotal'), max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(_('Discount Amount'), max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(_('Shipping Cost'), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('Total'), max_digits=10, decimal_places=2)

    # Social Impact tracking - Core to WWC mission
    total_impact_items = models.IntegerField(_('Total Impact Items'), default=0)
    impact_summary = models.JSONField(
        _('Impact Summary'),
        default=dict,
        help_text='Breakdown of impact by item type'
    )

    # Shipping Address
    shipping_first_name = models.CharField(_('First Name'), max_length=100)
    shipping_last_name = models.CharField(_('Last Name'), max_length=100)
    shipping_company = models.CharField(_('Company'), max_length=200, blank=True)
    shipping_address_1 = models.CharField(_('Address Line 1'), max_length=200)
    shipping_address_2 = models.CharField(_('Address Line 2'), max_length=200, blank=True)
    shipping_city = models.CharField(_('City'), max_length=100)
    shipping_state = models.CharField(_('State/Province'), max_length=100, blank=True)
    shipping_postal_code = models.CharField(_('Postal Code'), max_length=20)
    shipping_country = models.CharField(_('Country'), max_length=2, default='TN')

    # Billing Address (optional, if different from shipping)
    billing_same_as_shipping = models.BooleanField(_('Billing Same as Shipping'), default=True)
    billing_first_name = models.CharField(_('Billing First Name'), max_length=100, blank=True)
    billing_last_name = models.CharField(_('Billing Last Name'), max_length=100, blank=True)
    billing_company = models.CharField(_('Billing Company'), max_length=200, blank=True)
    billing_address_1 = models.CharField(_('Billing Address Line 1'), max_length=200, blank=True)
    billing_address_2 = models.CharField(_('Billing Address Line 2'), max_length=200, blank=True)
    billing_city = models.CharField(_('Billing City'), max_length=100, blank=True)
    billing_state = models.CharField(_('Billing State/Province'), max_length=100, blank=True)
    billing_postal_code = models.CharField(_('Billing Postal Code'), max_length=20, blank=True)
    billing_country = models.CharField(_('Billing Country'), max_length=2, blank=True)

    # Payment
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='stripe'
    )
    payment_id = models.CharField(_('Payment ID'), max_length=200, blank=True)
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)

    # Shipping tracking
    shipping_method = models.CharField(_('Shipping Method'), max_length=100, blank=True)
    tracking_number = models.CharField(_('Tracking Number'), max_length=100, blank=True)
    shipped_at = models.DateTimeField(_('Shipped At'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Delivered At'), null=True, blank=True)

    # Notes
    customer_notes = models.TextField(_('Customer Notes'), blank=True)
    admin_notes = models.TextField(_('Admin Notes'), blank=True)

    # Discount/Coupon
    coupon_code = models.CharField(_('Coupon Code'), max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """Generate unique order number: WWC-YYYYMMDD-XXXX"""
        today = timezone.now().strftime('%Y%m%d')
        prefix = f"WWC-{today}"

        # Get the last order number for today
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()

        if last_order:
            last_num = int(last_order.order_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"{prefix}-{new_num:04d}"

    @property
    def shipping_full_name(self):
        return f"{self.shipping_first_name} {self.shipping_last_name}"

    @property
    def shipping_full_address(self):
        parts = [self.shipping_address_1]
        if self.shipping_address_2:
            parts.append(self.shipping_address_2)
        parts.append(f"{self.shipping_postal_code} {self.shipping_city}")
        if self.shipping_state:
            parts.append(self.shipping_state)
        parts.append(self.shipping_country)
        return ', '.join(parts)


class OrderItem(models.Model):
    """Items within an order - captures state at time of purchase"""
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('Order')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Product')
    )
    producer = models.ForeignKey(
        Producer,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Producer')
    )

    # Capture product details at time of order
    product_name = models.CharField(_('Product Name'), max_length=200)
    product_sku = models.CharField(_('Product SKU'), max_length=50)

    quantity = models.PositiveIntegerField(_('Quantity'))
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('Subtotal'), max_digits=10, decimal_places=2)

    # Capture impact at order time (important for historical accuracy)
    impact_quantity = models.IntegerField(_('Impact Quantity'))
    impact_item = models.CharField(_('Impact Item'), max_length=100)
    impact_school = models.CharField(_('Impact School'), max_length=200)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.subtotal:
            self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """Discount coupon codes"""
    DISCOUNT_TYPE_CHOICES = [
        ('percent', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    ]

    code = models.CharField(_('Code'), max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(_('Discount Type'), max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    discount_value = models.DecimalField(_('Discount Value'), max_digits=8, decimal_places=2)
    min_order_amount = models.DecimalField(_('Minimum Order Amount'), max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField(_('Max Uses'), default=0, help_text='0 = unlimited')
    used_count = models.IntegerField(_('Used Count'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    valid_from = models.DateTimeField(_('Valid From'), null=True, blank=True)
    valid_until = models.DateTimeField(_('Valid Until'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'percent' else ' DT'})"

    def is_valid(self, order_amount=0):
        """Check if coupon is valid"""
        now = timezone.now()
        if not self.is_active:
            return False, 'Code promo inactif.'
        if self.valid_from and now < self.valid_from:
            return False, 'Code promo pas encore valide.'
        if self.valid_until and now > self.valid_until:
            return False, 'Code promo expiré.'
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False, 'Code promo épuisé.'
        if order_amount < self.min_order_amount:
            return False, f'Commande minimum de {self.min_order_amount} DT requise.'
        return True, 'ok'

    def calculate_discount(self, subtotal):
        """Calculate discount amount for given subtotal"""
        if self.discount_type == 'percent':
            return min(subtotal * self.discount_value / 100, subtotal)
        return min(self.discount_value, subtotal)


class ImpactEvent(models.Model):
    """
    Track real impact events funded by purchases.
    Shows transparency - what WWC did with the money from orders.
    """
    title = models.CharField(_('Title'), max_length=200)
    title_en = models.CharField(_('Title (English)'), max_length=200, blank=True)
    description = models.TextField(_('Description'))
    description_en = models.TextField(_('Description (English)'), blank=True)
    school = models.CharField(_('School'), max_length=200)
    date = models.DateField(_('Date'))
    items_delivered = models.IntegerField(_('Items Delivered'))
    item_type = models.CharField(_('Item Type'), max_length=100)
    photo = models.ImageField(_('Photo'), upload_to='impact/', blank=True, null=True)
    video_url = models.URLField(_('Video URL'), blank=True)
    funded_by_orders = models.ManyToManyField(
        Order,
        related_name='impact_events',
        blank=True,
        verbose_name=_('Funded By Orders')
    )
    is_published = models.BooleanField(_('Published'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Impact Event')
        verbose_name_plural = _('Impact Events')
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.date}"
