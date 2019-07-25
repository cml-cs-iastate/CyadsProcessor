import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CyadsProcessor.settings')

celery_app = Celery('downloader', redis_socket_connect_timeout=2, redis_socket_timeout=2)
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()