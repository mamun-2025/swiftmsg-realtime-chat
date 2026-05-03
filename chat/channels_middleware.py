
import jwt
import logging
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs

Logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token_key):
    # ফাংশনের ভেতরে ইম্পোর্ট করছি যাতে জ্যাঙ্গো রেডি হওয়ার পরই এটি কল হয়
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        # টোকেন ডিকোড করা
        payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if not user_id:
            return AnonymousUser()
            
        return User.objects.get(id=user_id)
        
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        Logger.warning("Expired or invalid JWT token provided for WebSocket.")
        return AnonymousUser()
    except User.DoesNotExist:
        Logger.warning(f"User with ID {user_id} not found from JWT token.")
        return AnonymousUser()
    except Exception as e:
        Logger.error(f"Unexpected error during token authentication: {e}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # scope['query_string'] থেকে নিরাপদ উপায়ে কুয়েরি বের করা
        query_string = scope.get('query_string', b'').decode('utf-8')
        
        # urllib.parse এর parse_qs ব্যবহার করা সবচেয়ে নিরাপদ এবং স্ট্যান্ডার্ড
        query_params = parse_qs(query_string)
        
        # কুয়েরি থেকে টোকেনটি বের করা
        token = query_params.get('token', [None])[0]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)