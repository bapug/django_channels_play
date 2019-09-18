from django.urls import path

from . import consumers

websocket_urlpatterns = [
    #url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
    path(r'ws/chat/<str:room_name>/', consumers.ChatConsumer),
    path(r'ws/comments/<str:group>/<str:slug>/', consumers.CommentConsumer),
]