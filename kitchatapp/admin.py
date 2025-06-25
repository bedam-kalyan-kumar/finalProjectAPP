from django.contrib import admin
from .models import Login, Post, Notification, Message, Comment, Like,Story

admin.site.register(Login)
admin.site.register(Post)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Story)