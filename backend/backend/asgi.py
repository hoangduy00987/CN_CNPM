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
<<<<<<< HEAD
from api.job.consumers import JobConsumer, ApplicationConsumer,NotificationJobConsumer
=======
from api.job.consumers import JobConsumer, ApplicationConsumer, JobExpiryNotificationConsumer
>>>>>>> 01f433557fd9ec82cd6ea9a96fc9cd4e0f6dc059

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

from api.job.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter([
            path('ws/updates/', JobConsumer.as_asgi()),  
            path('ws/new_application/', ApplicationConsumer.as_asgi()),
<<<<<<< HEAD
            path('ws/desired_job/', NotificationJobConsumer.as_asgi()),
=======
            path('ws/expired_job_notification/', JobExpiryNotificationConsumer.as_asgi()),
>>>>>>> 01f433557fd9ec82cd6ea9a96fc9cd4e0f6dc059
        ])
    ),
})
