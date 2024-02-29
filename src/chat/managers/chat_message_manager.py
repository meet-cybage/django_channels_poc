from django.db.models import Manager, QuerySet, Q, Case, When, Value, F, IntegerField, Subquery, OuterRef
from users.models import User


class ChatMessageQuerySet(QuerySet):

    def get_chat_message_users(self, content_type, user_id):
        conditions = [
            When(chat_room__object_id=user_id, then=F('chat_room__room_associated_member_id')),
            When(chat_room__room_associated_member_id=user_id, then=F('chat_room__object_id')),
        ]

        chat_message_queryset = self.filter(
            Q(chat_room__content_type=content_type, chat_room__object_id=user_id) |
            Q(chat_room__content_type=content_type, chat_room__room_associated_member_id=user_id)
        ).annotate(
            room_user_id=Case(
                *conditions,
                default=Value(None),
                output_field=IntegerField()
            )
        ).values("room_user_id", "chat_room_id", "message").distinct().order_by('-created_at')

        user_subquery = User.objects.filter(id=OuterRef('room_user_id')).values('username', 'first_name', 'last_name')

        # Final queryset to fetch the desired data
        results = chat_message_queryset.annotate(
            room_username=Subquery(user_subquery.values('username')[:1]),
            room_user_first_name=Subquery(user_subquery.values('first_name')[:1]),
            room_user_last_name=Subquery(user_subquery.values('last_name')[:1]),
        ).values('chat_room_id', 'room_user_id', 'room_username', 'room_user_first_name', 'room_user_last_name', 'message')

        return results


class ChatMessageManager(Manager):

    def get_queryset(self):
        return ChatMessageQuerySet(self.model, using=self._db) #Important
    
    def get_chat_message_users(self, content_type, user_id):
        return self.get_queryset().get_chat_message_users(content_type, user_id)
