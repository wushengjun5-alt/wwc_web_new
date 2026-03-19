"""
URL configuration for WWC Shop API v1
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import payments
from . import admin_views

# Create router for public API
router = DefaultRouter()

# Product routes
router.register(r'categories', views.ProductCategoryViewSet, basename='category')
router.register(r'producers', views.ProducerViewSet, basename='producer')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'boxes', views.ComposableBoxViewSet, basename='box')

# Cart routes
router.register(r'cart', views.CartViewSet, basename='cart')

# Order routes
router.register(r'orders', views.OrderViewSet, basename='order')

# Customer routes
router.register(r'addresses', views.CustomerAddressViewSet, basename='address')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

# Impact routes
router.register(r'impact-events', views.ImpactEventViewSet, basename='impact-event')

# Create router for admin API
admin_router = DefaultRouter()
admin_router.register(r'products', admin_views.AdminProductViewSet, basename='admin-product')
admin_router.register(r'categories/manage', admin_views.AdminCategoryManageViewSet, basename='admin-category-manage')
admin_router.register(r'producers/manage', admin_views.AdminProducerManageViewSet, basename='admin-producer-manage')

urlpatterns = [
    # Router URLs (public API)
    path('', include(router.urls)),

    # Admin API routes (protected by API key)
    path('admin/', include(admin_router.urls)),
    path('admin/categories/', admin_views.AdminCategoryListView.as_view(), name='admin-categories'),
    path('admin/producers/', admin_views.AdminProducerListView.as_view(), name='admin-producers'),
    path('admin/stats/', admin_views.AdminStatsView.as_view(), name='admin-stats'),
    path('admin/orders/', admin_views.AdminOrderListView.as_view(), name='admin-orders'),
    path('admin/orders/<str:order_number>/', admin_views.AdminOrderDetailView.as_view(), name='admin-order-detail'),

    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    # Customer dashboard
    path('customer/dashboard/', views.CustomerDashboardView.as_view(), name='customer-dashboard'),
    path('customer/profile/', views.CustomerProfileView.as_view(), name='customer-profile'),

    # Impact summary
    path('impact/summary/', views.ImpactSummaryView.as_view(), name='impact-summary'),

    # Auth
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Payments - Stripe (EUR only)
    path('payments/create-session/', payments.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payments/webhook/', payments.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payments/status/<str:order_number>/', payments.PaymentStatusView.as_view(), name='payment-status'),

    # Payments - Bank transfer (TND only)
    path('payments/bank-transfer/<str:order_number>/', payments.BankTransferInstructionsView.as_view(), name='bank-transfer-instructions'),
]
