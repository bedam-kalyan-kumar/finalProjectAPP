from django.urls import re_path
from kitchatapp import consumers

websocket_urlpatterns = [
    re_path(r'ws/call/(?P<user_id>\d+)/$', consumers.CallConsumer.as_asgi()),
]
