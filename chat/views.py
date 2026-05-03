from .admin import User
from .serializers import RegisterSerializer, UserSerializer, MessageSerializer, ConversationSerializer
from rest_framework import generics, viewsets, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Prefetch, Q 
from django.utils import timezone
from .models import User, Message, Conversation


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
         ).select_related('sender').order_by('timestamp')
      
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

      
# Additional feature: One to one chat history api
   @action(detail=False, methods=['get'], url_path='history/(?P<other_user_id>[^/.]+)')
   def chat_history(self, request, other_user_id=None):
      me = request.user 
      try:
         other_user = User.objects.get(id=other_user_id)
      except User.DoesNotExist:
         return Response({"error:": "User not found"}, status=status.HTTP_404_NOT_FOUND)

      conversation = Conversation.objects.filter(
         participants=me 
      ).filter(
         participants=other_user,
         is_group_chat=False
      ).first()

      if not conversation:
         return Response([], status=status.HTTP_200_OK)
      
      messages = conversation.messages.all().select_related('sender').order_by('timestamp')
      serializer = MessageSerializer(messages, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)