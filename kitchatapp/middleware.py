# kitchatapp/middleware.py
from django.utils import timezone

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            user.last_seen = timezone.now()
            user.is_online = True
            user.save(update_fields=['last_seen', 'is_online'])
        response = self.get_response(request)
        return response
