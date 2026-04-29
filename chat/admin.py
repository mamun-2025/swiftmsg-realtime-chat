from django.contrib import admin 
from .models import User, Conversation, Message

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
   list_display = ['id', 'username', 'email', 'phone_number', 'is_online']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
   list_display = ['id', 'is_group_chat', 'created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
   list_display = ['id', 'conversation', 'sender', 'timestamp', 'is_read']

   