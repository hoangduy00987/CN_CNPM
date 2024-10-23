"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from channels.auth import AuthMiddlewareStack
from api.job.consumers import JobConsumer, ApplicationConsumer, JobExpiryNotificationConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

from api.job.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter([
            path('ws/updates/', JobConsumer.as_asgi()),  # Đường dẫn WebSocket
            path('ws/new_application/', ApplicationConsumer.as_asgi()),
            path('ws/expired_job_notification/', JobExpiryNotificationConsumer.as_asgi()),
        ])
    ),
})
