# kitchatapp/templatetags/user_status.py
from django import template
from datetime import timedelta
from django.utils import timezone

register = template.Library()

@register.filter
def is_user_online(user):
    if not user.last_seen:
        return False
    return timezone.now() - user.last_seen < timedelta(minutes=5)
