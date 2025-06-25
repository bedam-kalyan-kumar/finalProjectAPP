# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginHistory
from django.utils.timezone import now

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LoginHistory.objects.create(
        user=user,
        session_key=request.session.session_key,
        ip_address=get_client_ip(request)
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
