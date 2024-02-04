

from django.urls import path
from chat.views import ChatView, ChatRoomView


urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("create/room", ChatRoomView.as_view(), name="chat_room")

]
