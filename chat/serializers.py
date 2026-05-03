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
   sender_detail = UserSerializer(source='sender', read_only=True)
   
   class Meta:
      model = Message
      fields = [
         'id', 'conversation', 'sender', 'sender_name', 'sender_detail',
         'content', 'message_type', 'file', 'timestamp', 'is_read'
         ]
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
         return {
               "id": last_msg.id,
               "content": last_msg.content,
               "sender_id": last_msg.sender.id,
               "sender_name": last_msg.sender.username,
               "timestamp": last_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_msg.timestamp else None,
               "is_read": last_msg.is_read
           }   
      return None
   
class ChatSerializer(serializers.ModelSerializer):
   user = UserSerializer(read_only=True)
   last_message = serializers.SerializerMethodField()

   class Meta:
      model = Conversation
      fields = ['id', 'user', 'last_message']

   def get_last_message(self, obj):
       last_msg = obj.get('last_message') if isinstance(obj, dict) else getattr(obj, 'last_message', None)
       if last_msg:
          return {
             "content": last_msg.content,
             "timestamp": last_msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if hasattr(last_msg, 'timestamp') else None,
             "is_read": last_msg.is_read
          }
       return None
   