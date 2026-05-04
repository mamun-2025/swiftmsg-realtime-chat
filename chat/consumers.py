
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import Message 

# Logger Configuration for production error tracking
User = get_user_model()
Logger = logging.getLogger(__name__)

class PrivateChatConsumer(AsyncWebsocketConsumer):
   async def connect(self):
      self.me = self.scope['user']

      # security check: Only authenticated users can connect to websocket.
      if not self.me or self.me.is_anonymous:
         Logger.warning("Unauthorized user tried to connect to WebSocket.")
         await self.close(code=4003) # 4003: Forbidden code 
         return 
      
      try:
         self.other_user_id = int(self.scope['url_route']['kwargs']['other_user_id'])

         # Block self-chat with myself
         if self.me.id == self.other_user_id:
            Logger.warning(f"User {self.me.id} tried to connect to self-chat.")
            await self.close(code=4000) # 4000: Bad Request code 
            return 
         
         # Check if the other user exists in the database 
         other_user_exists = await self.check_other_user_exists(self.other_user_id)
         if not other_user_exists:
            Logger.warning(f"User with ID{self.other_user_id} does not exist.")
            await self.close(code=4004) # 4004: Not found code 
            return
         
         # Make the room name unique and one-to-one perfect for private chat between two users 
         user_ids = sorted([int(self.me.id), self.other_user_id])
         self.room_group_name = f'private_chat_{user_ids[0]}_{user_ids[1]}'

         # Add the group join and set the online user status in the database 
         await self.user_online_status_db(True)
         await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name 
         )
         await self.accept()

         # Mark all messages seen by send the other user messages 
         await self.mark_messages_as_read()

         # Others user send the signal that I have read the messages.
         await self.channel_layer.group_send(
            self.room_group_name,
            {
               'type': 'message_read_handler',
               'reader_id': self.me.id 
            }
         )

         # Do group broadcast to other user that I am online now.
         await self.channel_layer.group_send(
            self.room_group_name,
            {
               'type': 'status_broadcast',
               'user_id': self.me.id,
               'status': 'online'
            }
         )
      except (ValueError, KeyError) as e:
         Logger.error(f"Invalid connection parameters: {e}")
         await self.close(code=4001) # 4001: Invalid parameters code 

   async def disconnect(self, close_code):
      if self.me and not self.me.is_anonymous:
         try:
            await self.user_online_status_db(False)

            if hasattr(self, 'room_group_name'):
               await self.channel_layer.group_send(
                  self.room_group_name,
                  {
                    'type': 'status_broadcast',
                    'user_id': self.me.id, 
                    'status': 'offline'
                  }
               )
               await self.channel_layer.group_discard(
                  self.room_group_name,
                  self.channel_name
               )
         except Exception as e:
            Logger.error(f"Error during disconnect for user {self.me.id}: {e}")
   
   # It will works when from client send the data to websocket.
   async def receive(self, text_data):
      try:
         data = json.loads(text_data)
      except json.JSONDecodeError as e:
         Logger.error(f"Invalid JSON received: {e}")
         return
      
      msg_type = data.get('type')

      # 1. Typing status handler 
      if msg_type == 'typing_status':
         await self.channel_layer.group_send(
            self.room_group_name,
            {
               'type': 'typing_handler',
               'typing': data.get('typing', False),
               'user_id': self.me.id 
            }
         )
      
      # 2. Mark messages as read/seen handler 
      elif msg_type == "mark_as_read":
         await self.mark_messages_as_read()
         await self.channel_layer.group_send(
            self.room_group_name,
            {
               'type': 'message_read_handler',
               'reader_id': self.me.id 
            }
         )

      # Send the new message and save the message 
      elif 'message' in data:
         message_content = data['message'].strip()
         if not message_content: # Block empty messages 
            return
         
         saved_msg = await self.save_private_message(message_content)

         if saved_msg:
            # Broadcast the new message to the real-time at the whole group (other user)
            await self.channel_layer.group_send(
               self.room_group_name,
               {
                  'type': 'chat_message',
                  'id': saved_msg['id'],
                  'message': message_content,
                  'sender_id': self.me.id,
                  'timestamp': saved_msg['timestamp']
               }
            )

   
# ----- Even Handlers Methods ----- #

   async def typing_handler(self, event):
      # Broadcast the typing status to the other user in the group but not to myself.
      if self.me.id != event['user_id']:
         await self.send(text_data=json.dumps({
            'type': 'typing_status',
            'typing': event['typing'],
            'user_id': event['user_id']
         }))

   async def message_read_handler(self, event):
      # Broadcast the message read/seen status to the other user connected in the group but not to myself.
      if self.me.id != event['reader_id']:
         await self.send(text_data=json.dumps({
            'type': 'message_read_update',
            'reader_id': event['reader_id']
         }))

   async def message_read_update(self, event):
      await self.send(text_data=json.dumps({
         'type': 'seen_status',
         'reader_id': event['reader_id']
      }))

   async def status_broadcast(self, event):
      await self.send(text_data=json.dumps({
         'type': 'user_online',
         'user_id': event['user_id'],
         'status': event['status']
      }))

   async def chat_message(self, event):
      await self.send(text_data=json.dumps({
         'type': 'new_message',
         'id': event['id'],
         'message': event['message'],
         'sender_id': event['sender_id'],
         'timestamp': event['timestamp']
      }))


# ----- Database Queries (Optimized & Async Safe) ----- #
   @database_sync_to_async
   def check_other_user_exists(self, user_id):
      return User.objects.filter(id=user_id).exists()
   
   @database_sync_to_async
   def user_online_status_db(self, is_online):
      User.objects.filter(id=self.me.id).update(
         is_online=is_online,
         last_seen=timezone.now() if not is_online else self.me.last_seen 
      )

   @database_sync_to_async
   def save_private_message(self, message_text):
      try:
         other_user = User.objects.get(id=self.other_user_id)
         message = Message.objects.create(
            sender=self.me,
            receiver=other_user,
            content=message_text
         )
         return {
            'id': message.id,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(message, 'timestamp') else timezone.now().strftime('%Y-%m-%d %H:%M:%S')
         }
      
      except ObjectDoesNotExist:
         Logger.error(f"Cannot save message. Receiver with ID {self.other_user_id} does not exist.")
         return None
      
      except Exception as e:
         Logger.error(f"Error saving message: {e}")
         return None 
      
   @database_sync_to_async
   def mark_messages_as_read(self):
      try:
         Message.objects.filter(
            sender_id=self.other_user_id,
            receiver_id=self.me.id,
            is_read=False
         ).update(is_read=True)
      except Exception as e:
         Logger.error(f"Error marking messages as read: {e}")
         return 0