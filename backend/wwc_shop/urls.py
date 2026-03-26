"""
URL configuration for WWC Shop
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.http import FileResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
import os


def serve_frontend(request):
    """Serve the standalone frontend HTML file"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'index.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_product_page(request):
    """Serve the product detail HTML file"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'product.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_checkout_page(request):
    """Serve the checkout HTML file"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'checkout.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_login_page(request):
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'login.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_account_page(request):
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'account.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_reset_password_page(request):
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'reset-password.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_verify_email_page(request):
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'verify-email.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_cart_page(request):
    """Serve the cart page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'cart.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_order_success_page(request):
    """Serve the order success / confirmation page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'order-success.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_impact_page(request):
    """Serve the public impact page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'impact.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_donate_page(request):
    """Serve the donation page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'donate.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_box_builder_page(request):
    """Serve the composable box builder page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'box-builder.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_order_detail_page(request):
    """Serve the standalone order tracking/detail page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'order-detail.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_producer_page(request, slug=None):
    """Serve the producer public profile page"""
    frontend_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'producer.html')
    return FileResponse(open(frontend_path, 'rb'), content_type='text/html')


def serve_shop_admin_page(request, page='index'):
    """Serve shop admin HTML pages"""
    if not page.endswith('.html'):
        page = page + '.html'
    admin_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'admin', page)
    if os.path.exists(admin_path):
        return FileResponse(open(admin_path, 'rb'), content_type='text/html')
    # Default to index
    admin_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'admin', 'index.html')
    return FileResponse(open(admin_path, 'rb'), content_type='text/html')


def serve_shop_static(request, folder, filename):
    """Serve frontend static files (JS, CSS) from frontend/<folder>/"""
    file_path = os.path.join(settings.BASE_DIR.parent, 'frontend', folder, filename)
    content_types = {
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml',
    }
    ext = os.path.splitext(filename)[1]
    content_type = content_types.get(ext, 'application/octet-stream')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    from django.http import Http404
    raise Http404("File not found")


def serve_shop_admin_static(request, folder, filename):
    """Serve shop admin static files (CSS, JS)"""
    file_path = os.path.join(settings.BASE_DIR.parent, 'frontend', 'admin', folder, filename)
    content_types = {
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml',
    }
    ext = os.path.splitext(filename)[1]
    content_type = content_types.get(ext, 'application/octet-stream')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    from django.http import Http404
    raise Http404("File not found")


urlpatterns = [
    # Root redirect to shop frontend
    path('', RedirectView.as_view(url='/shop/', permanent=False), name='root'),

    # Shop frontend (served by Django to avoid CORS issues)
    path('shop/', serve_frontend, name='shop'),
    path('shop/product/', serve_product_page, name='shop-product'),
    path('shop/checkout/', serve_checkout_page, name='shop-checkout'),
    path('shop/login/', serve_login_page, name='shop-login'),
    path('shop/account/', serve_account_page, name='shop-account'),
    path('shop/reset-password/', serve_reset_password_page, name='shop-reset-password'),
    path('shop/verify-email/', serve_verify_email_page, name='shop-verify-email'),
    path('shop/cart/', serve_cart_page, name='shop-cart'),
    path('shop/order-success/', serve_order_success_page, name='shop-order-success'),
    path('shop/order-detail/', serve_order_detail_page, name='shop-order-detail'),
    path('shop/impact/', serve_impact_page, name='shop-impact'),
    path('shop/donate/', serve_donate_page, name='shop-donate'),
    path('shop/donate/success/', serve_donate_page, name='shop-donate-success'),
    path('shop/box-builder/', serve_box_builder_page, name='shop-box-builder'),
    path('shop/producers/<slug:slug>/', serve_producer_page, name='shop-producer'),

    # Shop admin (HTML interface for product management)
    # Static assets must come BEFORE the catch-all <str:page> route
    path('shop/admin/css/<str:filename>', serve_shop_admin_static, {'folder': 'css'}, name='shop-admin-css'),
    path('shop/admin/js/<str:filename>', serve_shop_admin_static, {'folder': 'js'}, name='shop-admin-js'),
    path('shop/admin/', serve_shop_admin_page, {'page': 'index'}, name='shop-admin'),
    path('shop/admin/<str:page>', serve_shop_admin_page, name='shop-admin-page'),

    # Frontend static files (shared JS utilities)
    path('shop/js/<str:filename>', serve_shop_static, {'folder': 'js'}, name='shop-js'),

    # Django Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include('api.urls')),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
