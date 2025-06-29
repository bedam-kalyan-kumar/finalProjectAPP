from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
class Login(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    image = models.ImageField(
    upload_to='profile_photos/',
    blank=False,
    null=True,
    default='profile_photos/default-profile.png'  # Ensure correct path
)


    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now) 
    created_at = models.DateTimeField(auto_now_add=True)
    gmail = models.EmailField(max_length=254, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    show_online_status = models.BooleanField(default=True)
    last_seen_visibility = models.CharField(
    max_length=20,
    choices=[('Everyone', 'Everyone'), ('Following', 'Only Following'), ('No One', 'No One')],
    default='Everyone'
)

    private_account = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['email']
    
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_following_count(self):
        """Returns the number of users this user is following."""
        return self.following.count()

    def get_followers_count(self):
        """Returns the number of users following this user."""
        return self.followers.count()
    def get_profile_pic_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/default-avatar.png'



from django.contrib.auth import get_user_model

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f"Post by {self.user.username} ({self.id})"



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,  # Allows system-generated notifications
        blank=True,
        related_name='triggered_notifications'
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    notification_type = models.CharField(
    max_length=50,
    choices=[
        ('like', 'Liked your post'),
        ('comment', 'Commented on your post'),
        ('follow', 'Followed you'),
        ('unfollow', 'Unfollowed you'),
        ('mention', 'Mentioned you'),
        ('message', 'Sent you a message'),
        ('post', 'Posted something'),
        ('profile', 'Updated their profile'),
    ],
    null=True,
    blank=True
)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'

    class Meta:
        ordering = ['-timestamp']



from django.db import models
class StoryReaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('haha', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]
    
    viewer = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='story_reactions')
    story = models.ForeignKey('Story', on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('viewer', 'story')

class Message(models.Model):
    sender = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(Login, on_delete=models.CASCADE, related_name='received_messages')
    sender_username = models.CharField(max_length=150, blank=True, null=True)
    recipient_username = models.CharField(max_length=150, blank=True, null=True)
    content = models.TextField()
    file = models.FileField(upload_to='messages/files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)  # Track if the message has been seen
    sender_profile_pic = models.CharField(max_length=255, blank=True, null=True)  # URL to sender's profile picture
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    seen = models.BooleanField(default=False)  # 👈 track seen status
    related_story = models.ForeignKey('Story', null=True, blank=True, on_delete=models.SET_NULL, related_name='related_messages')
    is_reaction = models.BooleanField(default=False)
    file = models.FileField(upload_to='messages/files/', null=True, blank=True)
    reaction_type = models.CharField(max_length=10, null=True, blank=True)
    def mark_as_seen(self):
        self.seen = True
        self.save()
    def save(self, *args, **kwargs):
        # Automatically set sender_username, recipient_username, and sender_profile_pic
        self.sender_username = self.sender.username
        self.recipient_username = self.recipient.username
        self.sender_profile_pic = self.sender.image.url if self.sender.image else '/static/default-avatar.png'
        super().save(*args, **kwargs)





from django.contrib.auth.models import User

class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refers to the custom user model
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        'Post', 
        on_delete=models.CASCADE, 
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes from the same user

class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refers to the custom user model
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        'Post', 
        on_delete=models.CASCADE, 
        related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.utils import timezone



from datetime import timedelta

class Story(models.Model):
    STORY_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.FileField(upload_to='stories/', null=True, blank=True)
    image = models.ImageField(upload_to='stories/', null=True, blank=True)
    video = models.FileField(upload_to='stories/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=STORY_TYPES)
    expires_at = models.DateTimeField()
    viewers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='viewed_stories', blank=True)
    messages = models.ManyToManyField('StoryMessage', related_name='story_messages', blank=True)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Story {self.id} by {self.user.username}"

class StoryMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} on {self.story}"
class StoryViewer(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    viewer = models.ForeignKey(Login, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('story', 'viewer')  # Ensures each viewer has only one entry per story

# models.py
class Follow(models.Model):
    follower = models.ForeignKey(
        Login, related_name='following', on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        Login, related_name='followers', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
    
class SharedPost(models.Model):
    sender = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="sent_shares")
    recipient = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="received_shares")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)
class ChatUserDelete(models.Model):
    deleter = models.ForeignKey(Login, related_name='deleted_chats', on_delete=models.CASCADE)
    deleted_user = models.ForeignKey(Login, related_name='was_deleted_in_chats', on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('deleter', 'deleted_user')

    def __str__(self):
        return f"{self.deleter.username} deleted chat with {self.deleted_user.username}"
 
# models.py
from django.db import models

class PendingOTP(models.Model):
    email = models.EmailField(blank=True, null=True)  # Email can be blank or null
    otp = models.CharField(max_length=6, null=False)  # OTP must be filled
    username = models.CharField(max_length=255, blank=True, null=True)  # Username can be blank or null
    password = models.CharField(max_length=255, blank=True, null=True)  # Password can be blank or null
    def __str__(self):
      return f"{self.email} - OTP: {self.otp}"

    
from django.db import models
from django.contrib.auth.models import User  # Make sure this import exists!

# Correct model definition
from django.contrib.auth.models import User

# models.py
class SearchHistory(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)  # login must be imported properly
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    

class LoginHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

