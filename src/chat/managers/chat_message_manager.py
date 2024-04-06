from collections import defaultdict
from itertools import chain
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db.models import Manager, QuerySet, Q, Case, When, Value, F, CharField, IntegerField, Subquery, OuterRef, JSONField, Func, BooleanField
from users.models import User


class ChatMessageQuerySet(QuerySet):

    def get_chat_message_users(self, content_type, user_id):
        """
        Returns a queryset of users having chat with a given user.
        """
        #Below queries will give results of the users based on the chat message only and not of the chat room
        # Subquery to get the latest message for each chat room
        latest_message_subquery = self.filter(
            chat_room_id=OuterRef('chat_room_id')
        ).order_by('-created_at').values('id')[:1]

        user_subquery = User.objects.filter(id=OuterRef('room_user_id')).annotate(
            full_name=Concat(F("first_name"), Value(" "), F("last_name"))
        ).values('username', 'full_name')

        conditions = [
            When(chat_room__object_id=user_id, then=F('chat_room__room_associated_member_id')),
            When(chat_room__room_associated_member_id=user_id, then=F('chat_room__object_id')),
        ]

        chat_message_results = self.filter(
            Q(chat_room__content_type=content_type, chat_room__object_id=user_id) |
            Q(chat_room__content_type=content_type, chat_room__room_associated_member_id=user_id)
        ).annotate(
            room_user_id=Case(
                *conditions,
                default=Value(None),
                output_field=IntegerField()
            )
        ).annotate(
            room_username=Subquery(user_subquery.values('username')[:1]),
            room_user_full_name=Subquery(user_subquery.values('full_name')[:1]),
        ).filter(
            id=Subquery(latest_message_subquery)
        ).values('chat_room_id', 'room_user_id', 'room_username', 'room_user_full_name', 'message', "created_at").order_by('-created_at', "chat_room_id")

        # below queries are used to fetch the data of the room users for whom messaging is not done
        message_room_ids = chat_message_results.values_list("chat_room_id", flat=True)

        room_conditions = [
            When(object_id=user_id, then=F('room_associated_member_id')),
            When(room_associated_member_id=user_id, then=F('object_id')),
        ]

        chat_room_without_message = apps.get_model('chat', 'ChatRoom').objects.exclude(
            id__in=message_room_ids
        ).filter(
            Q(content_type=content_type, object_id=user_id) | Q(content_type=content_type, room_associated_member_id=user_id)
        ).annotate(
            room_user_id=Case(
                *room_conditions,
                default=Value(None),
                output_field=IntegerField()
            ),
            chat_room_id=F("id"),
            message=Value('', output_field=CharField())
        ).annotate(
            room_username=Subquery(user_subquery.values('username')[:1]),
            room_user_full_name=Subquery(user_subquery.values('full_name')[:1]),
        ).values('chat_room_id', 'room_user_id', 'room_username', 'room_user_full_name', "message", "created_at").order_by('created_at')
        results = list(chain(chat_message_results, chat_room_without_message))
        return results
    
    def get_chat_message_groups(self, content_type, user_id, models):
        """
        Returns a queryset of group chat of a given user.
        """
        latest_message_subquery = self.filter(
            chat_room_id=OuterRef('chat_room_id')
        ).order_by('-created_at').values('id')[:1]

        chat_group_members = models.get("chat_group_members")
        user_group_ids = chat_group_members.objects.filter(user_id=user_id).values_list("group_id", flat=True).distinct()
        chat_messages_results = self.filter(chat_room__content_type=content_type, chat_room__object_id__in=user_group_ids).annotate(
                            group_id=F("chat_room__object_id"),
                            group_name=F("chat_room__group_room__group_name")
                        ).filter(
                            id=Subquery(latest_message_subquery)
                        ).values("chat_room_id", "group_id", "group_name", "message", "created_at").order_by("-created_at")
        
        # Below queries are used to fetch those groups of user where no chat was done
        message_room_ids = chat_messages_results.values_list("chat_room_id", flat=True)
        chat_room_without_message = apps.get_model('chat', 'ChatRoom').objects.exclude(
            id__in=message_room_ids
        ).filter(
            content_type=content_type,
            object_id__in=user_group_ids
        ).annotate(
            group_id=F("object_id"),
            group_name=F("group_room__group_name"),
            chat_room_id=F("id"),
            message=Value('', output_field=CharField())
        ).values("chat_room_id", "group_id", "group_name", "message", "created_at").order_by("created_at")
    
        ## Previous attempt to add group members in the api response but later found it wrong and unwanted in api response 
        # group_members = chat_group_members.objects.filter(group_id__in=user_group_ids).select_related('user')

        # # Construct a dictionary to store user details for each group ID
        # user_details_map = defaultdict(list)

        # # Populate the user details dictionary
        # for member in group_members:
        #     user_details_map[member.group_id].append({
        #         'user_id': member.user.id,
        #         'username': member.user.username,
        #         'full_name': f"{member.user.first_name} {member.user.last_name}"
        #     })

        # for message in chat_messages:
        #     message['user_details'] = user_details_map[message['group_id']]
        
        chat_messages = list(chain(chat_messages_results, chat_room_without_message))
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
    
    def get_specific_room_chat(self, room_id, user_id, start, end):
        chat_messages_queryset = self.filter(chat_room_id=room_id).values("id", "chat_room_id", "message", "sender_id").order_by("-created_at")[start: end]

        user_subquery = User.objects.filter(id=OuterRef('sender_id')).annotate(full_name=Concat(F("first_name"), Value(" "), F("last_name"))).values('username', 'full_name')

        chat_messages = chat_messages_queryset.annotate(
            is_current_user_sender=Case(
                When(sender_id=user_id, then=True),
                default=False,
                output_field=BooleanField()
            ),
            sender_username=Subquery(user_subquery.values('username')[:1]),
            sender_full_name=Subquery(user_subquery.values('full_name')[:1]),
        )
        return chat_messages

    
class ChatMessageManager(Manager):

    def get_queryset(self):
        return ChatMessageQuerySet(self.model, using=self._db) #Important
    
    def get_chat_message_users(self, content_type, user_id):
        return self.get_queryset().get_chat_message_users(content_type, user_id)
    
    def get_chat_message_groups(self, content_type, user_id, models):
        return self.get_queryset().get_chat_message_groups(content_type, user_id, models)
    
    def create_chat_message(self, sender, data):
        return self.get_queryset().create_chat_message(sender, data)
    
    def get_specific_room_chat(self, room_id, user_id, start, end):
        return self.get_queryset().get_specific_room_chat(room_id, user_id, start, end)
    
