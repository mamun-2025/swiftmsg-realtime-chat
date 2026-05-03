
from django.urls import re_path

# জ্যাঙ্গো রেডি হওয়ার পর যেন consumers লোড হয়, তাই এই ফাংশনটি ব্যবহার করা হয়েছে
def get_websocket_urlpatterns():
    from . import consumers
    return [
        re_path(r'ws/chat/(?P<other_user_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
    ]

websocket_urlpatterns = get_websocket_urlpatterns()