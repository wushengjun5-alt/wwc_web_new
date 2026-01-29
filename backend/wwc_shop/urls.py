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


urlpatterns = [
    # Root redirect to shop frontend
    path('', RedirectView.as_view(url='/shop/', permanent=False), name='root'),

    # Shop frontend (served by Django to avoid CORS issues)
    path('shop/', serve_frontend, name='shop'),

    # Admin
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
