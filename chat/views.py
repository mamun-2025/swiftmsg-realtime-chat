from .admin import User
from .serializers import RegisterSerializer, UserSerializer, MessageSerializer, ConversationSerializer
from rest_framework import generics, viewsets, permissions
from rest_framework.permissions import AllowAny
from .models import User, Message, Conversation
from django.db.models import Prefetch

# Create your views here.
class RegisterView(generics.CreateAPIView):
   queryset = User.objects.all()
   serializer_class = RegisterSerializer
   permission_classes = (AllowAny,)
   

class UserViewSet(viewsets.ModelViewSet):
   queryset = User.objects.all()
   serializer_class = UserSerializer
   permission_classes = [permissions.IsAuthenticated]


class MessageViewSet(viewsets.ModelViewSet):
   serializer_class = MessageSerializer
   permission_classes = [permissions.IsAuthenticated]

   def get_queryset(self):
      conversation_id = self.request.query_params.get('conversation_id')
      if conversation_id:
         return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user
         ).select_related('sender')
      
      return Message.objects.none()

   def perform_create(self, serializer):
      serializer.save(sender=self.request.user)


class ConversationViewSet(viewsets.ModelViewSet):
   serializer_class = ConversationSerializer
   permission_classes = [permissions.IsAuthenticated]

   def get_queryset(self):
      return Conversation.objects.filter(
         participants=self.request.user
      ).prefetch_related(
         'participants',
         Prefetch(
            'messages',
            queryset=Message.objects.select_related('sender').order_by('-timestamp')
         )
      ).distinct()
   
   def perform_create(self, serializer):
      instance = serializer.save()
      instance.participants.add(self.request.user)

      

