from rest_framework import serializers
from .models import User, Message, Conversation

class RegisterSerializer(serializers.ModelSerializer):
   password = serializers.CharField(write_only=True, min_length=8)

   class Meta:
      model = User
      fields = ['username', 'email', 'password', 'phone_number']

   def create(self, validated_data):
      user = User.objects.create_user(
         **validated_data
      )
      return user

class UserSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = ['id', 'username', 'phone_number', 'profile_pic', 'is_online', 'last_seen']


class MessageSerializer(serializers.ModelSerializer):
   sender_name = serializers.ReadOnlyField(source='sender.username')
   class Meta:
      model = Message
      fields = ['id', 'conversation', 'sender', 'sender_name', 'content', 'message_type', 'file', 'timestamp', 'is_read']
      read_only_fields = ['timestamp', 'sender']


class ConversationSerializer(serializers.ModelSerializer):
   participants = UserSerializer(many=True, read_only=True)
   last_message = serializers.SerializerMethodField()

   class Meta:
      model = Conversation
      fields = ['id', 'participants', 'is_group_chat', 'created_at', 'last_message']

   def get_last_message(self, obj):
      last_msg = obj.messages.order_by('-timestamp').first()
      if last_msg:
         return MessageSerializer(last_msg).data
      return None
   