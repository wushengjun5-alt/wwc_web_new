from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum


class Country(models.Model):
    name = models.CharField(_('Name (FR)'), max_length=100)
    name_en = models.CharField(_('Name (EN)'), max_length=100, blank=True)
    name_ar = models.CharField(_('Name (AR)'), max_length=100, blank=True)
    slug = models.SlugField(unique=True)
    flag_emoji = models.CharField(_('Flag Emoji'), max_length=10, default='🌍')
    description = models.TextField(_('Description (FR)'), blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.IntegerField(_('Display Order'), default=0)

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class DonationProject(models.Model):
    CATEGORY_CHOICES = [
        ('food', _('Alimentation')),
        ('infrastructure', _('Infrastructure')),
        ('sports', _('Sport')),
        ('education', _('Éducation')),
        ('health', _('Santé')),
        ('other', _('Autre')),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(_('Title (FR)'), max_length=200)
    title_en = models.CharField(_('Title (EN)'), max_length=200, blank=True)
    description = models.TextField(_('Description (FR)'), blank=True)
    description_en = models.TextField(_('Description (EN)'), blank=True)
    school = models.CharField(_('School / Beneficiary'), max_length=200, blank=True)
    category = models.CharField(_('Category'), max_length=30, choices=CATEGORY_CHOICES, default='other')
    goal_amount = models.DecimalField(_('Goal Amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=3, default='TND')
    image = models.ImageField(_('Image'), upload_to='donation_projects/', blank=True, null=True)
    deadline = models.DateField(_('Deadline'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    is_featured = models.BooleanField(_('Featured'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Donation Project')
        verbose_name_plural = _('Donation Projects')
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    @property
    def raised_amount(self):
        result = self.donations.filter(status='completed').aggregate(total=Sum('amount'))
        return result['total'] or 0

    @property
    def progress_percent(self):
        if not self.goal_amount:
            return 0
        pct = float(self.raised_amount) / float(self.goal_amount) * 100
        return min(round(pct, 1), 100)

    @property
    def donor_count(self):
        return self.donations.filter(status='completed').count()


class Donation(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('stripe', _('Carte bancaire (Stripe)')),
        ('bank_transfer', _('Virement bancaire')),
    ]
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('completed', _('Complété')),
        ('failed', _('Échoué')),
    ]

    project = models.ForeignKey(DonationProject, on_delete=models.CASCADE, related_name='donations')
    donor_name = models.CharField(_('Donor Name'), max_length=200, blank=True)
    donor_email = models.EmailField(_('Donor Email'), blank=True)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=3, default='TND')
    payment_method = models.CharField(_('Payment Method'), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='stripe')
    payment_id = models.CharField(_('Payment ID'), max_length=200, blank=True)
    message = models.TextField(_('Message'), blank=True)
    is_anonymous = models.BooleanField(_('Anonymous'), default=False)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Donation')
        verbose_name_plural = _('Donations')
        ordering = ['-created_at']

    def __str__(self):
        name = 'Anonyme' if self.is_anonymous else (self.donor_name or self.donor_email or 'Inconnu')
        return f'{name} — {self.amount} {self.currency} → {self.project.title}'
