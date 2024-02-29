

from django.urls import path
from chat.views import ChatView, ChatRoomView, ChatUsersAndGroups


urlpatterns = [
    path("", ChatView.as_view(), name="chat"),
    path("create/room", ChatRoomView.as_view(), name="chat_room"),
    path("get/chat_users_and_groups", ChatUsersAndGroups.as_view(), name="chat_users_and_groups")

]
