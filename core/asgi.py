import os
import django
from django.core.asgi import get_asgi_application

# ১. জ্যাঙ্গো এনভায়রনমেন্ট সেটআপ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# ২. জ্যাঙ্গো অ্যাপ্লিকেশন লোড এবং সেটআপ করা (অন্য কোনো ইম্পোর্টের আগে)
django_asgi_app = get_asgi_application()
django.setup()

# ৩. জ্যাঙ্গো পুরোপুরি লোড হওয়ার পর চ্যাট রাউটিং ও মিডলওয়্যার ইম্পোর্ট
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.channels_middleware import JWTAuthMiddleware
import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    
    "websocket": JWTAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns 
        )
    ),
})