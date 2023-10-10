from django.urls import re_path

from thread import consumers

websocket_urlpatterns = [
    re_path(r'ws/threads/$', consumers.ThreadConsumer.as_asgi()),
]
