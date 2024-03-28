from collections import defaultdict
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
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

        # user_subquery = User.objects.filter(id=OuterRef('room_user_id')).values("username", "first_name", "last_name")
        user_subquery = User.objects.filter(id=OuterRef('room_user_id')).annotate(full_name=Concat(F("first_name"), Value(" "), F("last_name"))).values('username', 'full_name')

        # Final queryset to fetch the desired data
        # results = chat_message_queryset.annotate(
        #     room_username=Subquery(user_subquery.values('username')[:1]),
        #     room_user_first_name=Subquery(user_subquery.values('first_name')[:1]),
        #     room_user_last_name=Subquery(user_subquery.values('last_name')[:1]),
        # ).values('chat_room_id', 'room_user_id', 'room_username', 'room_user_first_name', 'room_user_last_name', 'message')

        results = chat_message_queryset.annotate(
            room_username=Subquery(user_subquery.values('username')[:1]),
            room_user_full_name=Subquery(user_subquery.values('full_name')[:1]),
        ).values('chat_room_id', 'room_user_id', 'room_username', 'room_user_full_name', 'message')

        return results
    
    def get_chat_message_groups(self, content_type, user_id, models):
        chat_group_members = models.get("chat_group_members")
        user_group_ids = chat_group_members.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
        chat_messages = self.filter(chat_room__content_type=content_type, chat_room__object_id__in=user_group_ids).annotate(
                            group_id=F("chat_room__object_id"),
                            group_name=F("chat_room__group_room__group_name")
                        ).values("chat_room_id", "group_id", "group_name", "message")
        
    
        group_members = chat_group_members.objects.filter(group_id__in=user_group_ids).select_related('user')

        # Construct a dictionary to store user details for each group ID
        user_details_map = defaultdict(list)

        # Populate the user details dictionary
        for member in group_members:
            user_details_map[member.group_id].append({
                'user_id': member.user.id,
                'username': member.user.username,
                'full_name': f"{member.user.first_name} {member.user.last_name}"
            })

        for message in chat_messages:
            message['user_details'] = user_details_map[message['group_id']]
        
        return chat_messages

    def create_chat_message(self, sender, data):
        # group_id = data['group_id']

        # if group_id:
        #     chat_group_model = apps.get_model('chat', 'ChatGroup')
        #     group_content_type = ContentType.objects.get_for_model(chat_group_model)
        # else:
        #     user_content_type = ContentType.objects.get_for_model(User)  

        chat_message = self.create(
            message=data.get("message"),
            chat_room_id=data.get("room_id"),
            sender_id=sender
        )
        return chat_message


class ChatMessageManager(Manager):

    def get_queryset(self):
        return ChatMessageQuerySet(self.model, using=self._db) #Important
    
    def get_chat_message_users(self, content_type, user_id):
        return self.get_queryset().get_chat_message_users(content_type, user_id)
    
    def get_chat_message_groups(self, content_type, user_id, models):
        return self.get_queryset().get_chat_message_groups(content_type, user_id, models)
    
    def create_chat_message(self, sender, data):
        return self.get_queryset().create_chat_message(sender, data)
