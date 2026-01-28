"""
URL configuration for WWC Shop API v1
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import payments

# Create router
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

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Checkout
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    # Customer dashboard
    path('customer/dashboard/', views.CustomerDashboardView.as_view(), name='customer-dashboard'),
    path('customer/profile/', views.CustomerProfileView.as_view(), name='customer-profile'),

    # Impact summary
    path('impact/summary/', views.ImpactSummaryView.as_view(), name='impact-summary'),

    # Auth
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),

    # Payments
    path('payments/create-intent/', payments.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('payments/create-session/', payments.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('payments/webhook/', payments.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payments/status/<str:order_number>/', payments.PaymentStatusView.as_view(), name='payment-status'),
]
