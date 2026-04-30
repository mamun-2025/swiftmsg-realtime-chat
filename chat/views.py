from .admin import User
from .serializers import RegisterSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny

# Create your views here.
class RegisterView(generics.CreateAPIView):
   queryset = User.objects.all()
   serializer_class = RegisterSerializer
   permission_classes = (AllowAny,)
   
