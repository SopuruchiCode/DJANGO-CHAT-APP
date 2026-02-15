from django.urls import re_path
from .consumers import ChatConsumer, ChatSearchConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/$", ChatConsumer.as_asgi()),
    re_path(r"ws/chat-search/$", ChatSearchConsumer.as_asgi())
    # re_path(r"ws/chat/(?P<friend_username>[A-Za-z0-9_]*)/$", ChatConsumer.as_asgi())
]