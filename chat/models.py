from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User Model
class User(AbstractUser):
   phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
   profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
   bio = models.TextField(max_length=500, blank=True)
   last_seen = models.DateTimeField(auto_now=True)
   is_online = models.BooleanField(default=False)

   def __str__(self):
      return self.username
   
# 2. Conversation Model
class Conversation(models.Model):
   participants = models.ManyToManyField(User, related_name='conversations')
   is_group_chat = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return f"Chat_ID: {self.id} - Group: {self.is_group_chat}"
   
# 3. Message Model 
class Message(models.Model):
   MESSAGE_TYPES = (
      ('text', 'Text'),
      ('image', 'Image'),
      ('video', 'Video'),
      ('file', 'File'),
   )
   conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
   sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
   content = models.TextField(blank=True)
   message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
   file = models.FileField(upload_to='chat_media/', null=True, blank=True)
   timestamp = models.DateTimeField(auto_now_add=True)
   is_read = models.BooleanField(default=False)

   class Meta:
      ordering = ['timestamp']

   def __str__(self):
      return f"{self.sender.username}: {self.content[:20]}"
   
   
