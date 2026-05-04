import pytest 
from django.contrib.auth.models import User
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_chat_room_list_unauthorized():
   client = APIClient()
   response = client.get('/api/conversations/')
   assert response.status_code == 401 
   