"""
Admin API Key Authentication for WWC Shop

This module provides secure authentication for admin API endpoints using
a shared secret (API key) stored in Django settings and WordPress options.
"""

from rest_framework import authentication, exceptions
from django.conf import settings


class AdminAPIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that validates admin API keys.

    The API key should be sent in the Authorization header:
    Authorization: Api-Key YOUR_SECRET_KEY

    Configure in Django settings:
    ADMIN_API_KEY = 'your-secure-random-key'
    """

    keyword = 'Api-Key'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2:
            return None

        if parts[0] != self.keyword:
            return None

        api_key = parts[1]

        return self.authenticate_credentials(api_key)

    def authenticate_credentials(self, key):
        """
        Validate the API key against the configured admin key.
        Returns a tuple of (None, key) on success (no user object needed).
        """
        admin_api_key = getattr(settings, 'ADMIN_API_KEY', None)

        if not admin_api_key:
            raise exceptions.AuthenticationFailed(
                'Admin API key not configured on server'
            )

        if key != admin_api_key:
            raise exceptions.AuthenticationFailed('Invalid admin API key')

        # Return None for user (no specific user), and the key as auth info
        return (None, key)

    def authenticate_header(self, request):
        return self.keyword


class IsAdminAPIKeyAuthenticated:
    """
    Permission class that requires admin API key authentication.
    Also allows Django staff/superusers via session auth.
    """

    def has_permission(self, request, view):
        # Check if authenticated via API key
        if request.auth and isinstance(request.auth, str):
            # API key authentication was successful
            return True

        # Also allow Django staff/superusers
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or request.user.is_superuser

        return False
