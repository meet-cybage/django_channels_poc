from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from chat.managers.chat_group_manager import ChatGroupManager
from chat.managers.chat_message_manager import ChatMessageManager
from commons.models import TimeBaseModel
from chat.managers.chat_room_manager import ChatRoomManager


User = get_user_model()
# Create your models here.
class ChatRoom(TimeBaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    room_associated_member = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    objects = ChatRoomManager()


class ChatGroup(TimeBaseModel):
    group_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.ManyToManyField(User, through="ChatGroupMembers")
    chat_room = GenericRelation(ChatRoom, related_query_name='group_room')

    objects = ChatGroupManager()


class ChatGroupMembers(TimeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)


class ChatMesssage(TimeBaseModel):
    message = models.TextField()
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = ChatMessageManager()
