"""
Celery configuration for WWC Shop
"""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wwc_shop.settings')

app = Celery('wwc_shop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
