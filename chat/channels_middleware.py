
import jwt
import logging
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token_key):
    # জ্যাঙ্গো পুরোপুরি লোড হওয়ার পর মডেল ইম্পোর্ট হবে
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        # SimpleJWT সাধারণত settings.SECRET_KEY ব্যবহার করে HS256 অ্যালগরিদমে টোকেন সাইন করে।
        # এখানে algorithms=['HS256'] দিয়ে ডিকোড করা হচ্ছে।
        payload = jwt.decode(token_key, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if not user_id:
            return AnonymousUser()
            
        return User.objects.get(id=user_id)
        
    except Exception as e:
        # যেকোনো এরর (যেমন: Expired, Invalid Token, বা Signature mismatch) হলে 
        # ক্র্যাশ না করে নিরাপদে AnonymousUser রিটার্ন করবে।
        logger.warning(f"JWT Auth failed: {e}")
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # কুয়েরি স্ট্রিং থেকে নিরাপদে টোকেন বের করা
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        
        # 'token' কুয়েরি প্যারামিটারটি খোঁজা
        token = query_params.get('token', [None])[0]

        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)