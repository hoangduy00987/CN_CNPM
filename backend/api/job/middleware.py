from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework.exceptions import AuthenticationFailed
from channels.db import database_sync_to_async
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()

if not settings.configured:
    raise ImproperlyConfigured("Django settings are not configured. Make sure DJANGO_SETTINGS_MODULE is set.")

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()
    
class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Lấy token từ query string
        query_string = scope['query_string'].decode('utf-8')
        token = None
        if 'token=' in query_string:
            token = query_string.split('token=')[1]

        # Nếu có token, xác thực người dùng
        if token:
            try:
                UntypedToken(token)  # Kiểm tra tính hợp lệ của token
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = await get_user(decoded_data['user_id'])
                scope['user'] = user
            except (AuthenticationFailed, KeyError):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
