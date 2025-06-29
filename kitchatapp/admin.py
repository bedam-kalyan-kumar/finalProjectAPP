from django.contrib import admin
from .models import Login, Post, Notification, Message, Comment, Like,Story,StoryReaction,StoryMessage,Follow,ChatUserDelete,SearchHistory,LoginHistory,PendingOTP
admin.site.register(Login)
admin.site.register(Post)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Story)
admin.site.register(StoryReaction)
admin.site.register(StoryMessage)
admin.site.register(Follow)
admin.site.register(ChatUserDelete)
admin.site.register(SearchHistory)
admin.site.register(LoginHistory)
admin.site.register(PendingOTP)

