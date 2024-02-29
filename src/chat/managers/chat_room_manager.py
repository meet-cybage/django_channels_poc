from django.db.models import Manager, QuerySet, Q


class ChatRoomQuerySet(QuerySet):

    def get_user_room(self, content_type, user_1, user_2):
        return self.filter(
            Q(content_type=content_type, object_id=user_1, room_associated_member_id=user_2) |
            Q(content_type=content_type, object_id=user_2, room_associated_member_id=user_1)
        )


class ChatRoomManager(Manager):

    def get_queryset(self):
        return ChatRoomQuerySet(self.model, using=self._db) #Important
    
    def get_user_room(self, content_type, user_1, user_2):
        return self.get_queryset().get_user_room(content_type, user_1, user_2)
