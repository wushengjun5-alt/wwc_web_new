"""
WSGI config for WWC Shop project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wwc_shop.settings')

application = get_wsgi_application()
