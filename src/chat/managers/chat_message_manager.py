from collections import defaultdict
from django.db.models import Manager, QuerySet, Q, Case, When, Value, F, IntegerField, Subquery, OuterRef, JSONField, Func
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
    
    def get_chat_message_groups(self, content_type, user_id, models):
        chat_group_members = models.get("chat_group_members")
        user_group_ids = chat_group_members.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
        chat_messages = self.filter(chat_room__content_type=content_type, chat_room__object_id__in=user_group_ids).annotate(
                            group_id=F("chat_room__object_id")
                        ).values("chat_room_id", "group_id", "message")
        
    
        group_members = chat_group_members.objects.filter(group_id__in=user_group_ids).select_related('user')

        # Construct a dictionary to store user details for each group ID
        user_details_map = defaultdict(list)

        # Populate the user details dictionary
        for member in group_members:
            user_details_map[member.group_id].append({
                'username': member.user.username,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name
            })

        for message in chat_messages:
            message['user_details'] = user_details_map[message['group_id']]
        
        return chat_messages        


class ChatMessageManager(Manager):

    def get_queryset(self):
        return ChatMessageQuerySet(self.model, using=self._db) #Important
    
    def get_chat_message_users(self, content_type, user_id):
        return self.get_queryset().get_chat_message_users(content_type, user_id)
    
    def get_chat_message_groups(self, content_type, user_id, models):
        return self.get_queryset().get_chat_message_groups(content_type, user_id, models)
