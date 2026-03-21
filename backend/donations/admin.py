from django.contrib import admin
from .models import Country, DonationProject, Donation


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['flag_emoji', 'name', 'slug', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DonationProject)
class DonationProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'category', 'goal_amount', 'currency', 'is_active', 'is_featured', 'deadline']
    list_filter = ['country', 'category', 'is_active', 'is_featured']
    list_editable = ['is_active', 'is_featured']
    search_fields = ['title', 'school']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'donor_email', 'amount', 'currency', 'project', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'currency']
    list_editable = ['status']
    search_fields = ['donor_name', 'donor_email', 'project__title']
    readonly_fields = ['created_at', 'updated_at']
