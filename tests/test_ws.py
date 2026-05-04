
import pytest
from channels.testing import WebsocketCommunicator
from core.asgi import application
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from channels.db import database_sync_to_async

User = get_user_model()

def create_test_user():
    User.objects.filter(username__in=["testuser_ws", "other_user_ws"]).delete()
    user1 =  User.objects.create_user(
        username="testuser_ws",
        email="ws@test.com",
        password="password123"
    )
    user2 = User.objects.create_user(
        username="other_user_ws",
        email="ws2@test.com",
        password="password123"
    )
    refresh = RefreshToken.for_user(user1)
    access_token = str(refresh.access_token)

    return user2.id, access_token

@pytest.fixture(autouse=True)
def override_channel_layer(settings):
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_connection():

    other_user_id, access_token = await database_sync_to_async(create_test_user)()
    path = f"/ws/chat/{other_user_id}/?token={access_token}"
    communicator = WebsocketCommunicator(application, path)

    connected, subprotocol = await communicator.connect(timeout=10)

    assert connected

    await communicator.disconnect()

    