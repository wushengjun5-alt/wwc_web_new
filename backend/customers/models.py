"""
Customer models for WWC Shop - Wallah We Can E-Commerce Platform

Includes: Customer profiles for B2C and B2B with impact tracking
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Customer(models.Model):
    """
    Extended user profile for B2C and B2B customers.
    Tracks cumulative impact from purchases.
    """
    CUSTOMER_TYPE_CHOICES = [
        ('individual', _('Individual Customer (B2C)')),
        ('company', _('Company (B2B)')),
    ]

    LANGUAGE_CHOICES = [
        ('fr', _('French')),
        ('en', _('English')),
        ('ar', _('Arabic')),
    ]

    CURRENCY_CHOICES = [
        ('TND', _('Tunisian Dinar')),
        ('EUR', _('Euro')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name=_('User')
    )
    customer_type = models.CharField(
        _('Customer Type'),
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='individual'
    )

    # Personal info
    phone = models.CharField(_('Phone'), max_length=20, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)

    # Company-specific fields (for B2B)
    company_name = models.CharField(_('Company Name'), max_length=200, blank=True)
    company_tax_id = models.CharField(_('Company Tax ID'), max_length=50, blank=True)
    company_address = models.TextField(_('Company Address'), blank=True)
    company_contact_name = models.CharField(_('Contact Person'), max_length=200, blank=True)

    # Default shipping address
    default_shipping_address_1 = models.CharField(_('Address Line 1'), max_length=200, blank=True)
    default_shipping_address_2 = models.CharField(_('Address Line 2'), max_length=200, blank=True)
    default_shipping_city = models.CharField(_('City'), max_length=100, blank=True)
    default_shipping_state = models.CharField(_('State/Province'), max_length=100, blank=True)
    default_shipping_postal_code = models.CharField(_('Postal Code'), max_length=20, blank=True)
    default_shipping_country = models.CharField(_('Country'), max_length=2, default='TN')

    # Impact tracking - Core to WWC mission
    total_purchases = models.DecimalField(
        _('Total Purchases'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total_orders = models.IntegerField(_('Total Orders'), default=0)
    total_impact_items = models.IntegerField(
        _('Total Impact Items'),
        default=0,
        help_text='Total items donated through purchases (e.g., energy bars)'
    )
    impact_breakdown = models.JSONField(
        _('Impact Breakdown'),
        default=dict,
        help_text='Breakdown of impact by item type'
    )

    # Preferences
    preferred_currency = models.CharField(
        _('Preferred Currency'),
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='TND'
    )
    preferred_language = models.CharField(
        _('Preferred Language'),
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='fr'
    )

    # Marketing
    newsletter_subscribed = models.BooleanField(_('Newsletter Subscribed'), default=False)
    accepts_marketing = models.BooleanField(_('Accepts Marketing'), default=False)

    # Verification
    email_verified = models.BooleanField(_('Email Verified'), default=False)
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        if self.customer_type == 'company' and self.company_name:
            return f"{self.company_name} ({self.user.email})"
        return self.user.email

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def is_b2b(self):
        return self.customer_type == 'company'

    def update_impact_stats(self):
        """Update impact statistics from completed orders"""
        from orders.models import Order

        completed_orders = Order.objects.filter(
            user=self.user,
            status__in=['paid', 'processing', 'shipped', 'delivered']
        )

        self.total_orders = completed_orders.count()
        self.total_purchases = sum(order.total for order in completed_orders)

        # Aggregate impact
        impact_breakdown = {}
        total_impact = 0

        for order in completed_orders:
            for item_type, quantity in order.impact_summary.items():
                impact_breakdown[item_type] = impact_breakdown.get(item_type, 0) + quantity
                total_impact += quantity

        self.impact_breakdown = impact_breakdown
        self.total_impact_items = total_impact
        self.save()


class CustomerAddress(models.Model):
    """
    Additional saved addresses for customers.
    Allows customers to save multiple shipping/billing addresses.
    """
    ADDRESS_TYPE_CHOICES = [
        ('shipping', _('Shipping')),
        ('billing', _('Billing')),
        ('both', _('Both')),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name=_('Customer')
    )
    address_type = models.CharField(
        _('Address Type'),
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='both'
    )
    is_default = models.BooleanField(_('Default Address'), default=False)

    # Address fields
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    company = models.CharField(_('Company'), max_length=200, blank=True)
    address_1 = models.CharField(_('Address Line 1'), max_length=200)
    address_2 = models.CharField(_('Address Line 2'), max_length=200, blank=True)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State/Province'), max_length=100, blank=True)
    postal_code = models.CharField(_('Postal Code'), max_length=20)
    country = models.CharField(_('Country'), max_length=2, default='TN')
    phone = models.CharField(_('Phone'), max_length=20, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Customer Address')
        verbose_name_plural = _('Customer Addresses')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}"

    def save(self, *args, **kwargs):
        # Ensure only one default address per type per customer
        if self.is_default:
            CustomerAddress.objects.filter(
                customer=self.customer,
                address_type=self.address_type,
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        parts = [self.address_1]
        if self.address_2:
            parts.append(self.address_2)
        parts.append(f"{self.postal_code} {self.city}")
        if self.state:
            parts.append(self.state)
        parts.append(self.country)
        return ', '.join(parts)


class Wishlist(models.Model):
    """Customer wishlist for products"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name=_('Customer')
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name=_('Product')
    )
    added_at = models.DateTimeField(_('Added At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        unique_together = ['customer', 'product']

    def __str__(self):
        return f"{self.customer} - {self.product}"


# Signal to create Customer profile when User is created
@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    if hasattr(instance, 'customer'):
        instance.customer.save()
