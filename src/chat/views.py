import json
from django.db import transaction
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from users.models import User
from chat.models import ChatGroup, ChatGroupMembers, ChatMesssage, ChatRoom

# Create your views here.


class ChatView(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, "chat/chat.html")
        # return HttpResponse("Successfully Logged In!!!!!", content_type="text/plain")


class ChatRoomView(View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        
        if data.get("room_type") == "Users":
            user_id = data.get("users")
            content_type = ContentType.objects.get_for_model(User)

            chat_room = ChatRoom.objects.get_user_room(content_type, request.user.id, user_id).first()

            if not chat_room:
                chat_room = ChatRoom.objects.create(
                    content_type=content_type,
                    object_id=user_id,
                    room_associated_member_id=request.user.id
                )
                
            return JsonResponse({
                "room_id": chat_room.id, 
                "user": chat_room.content_object.id,
                "full_name": f"{chat_room.content_object.first_name} {chat_room.content_object.last_name}",
                "username": chat_room.content_object.username
                })
        else:
            content_type = ContentType.objects.get_for_model(ChatGroup)
            group_name=data.get("group_name")
            users=data.get("users")
            chat_group = ChatGroup.objects.filter(group_name=group_name).first()

            if not chat_group:
                chat_group = ChatGroup.objects.create(
                    group_name=group_name,
                )
                chat_room = ChatRoom.objects.create(
                    content_type=content_type,
                    object_id=chat_group.id,
                    room_associated_member_id=request.user.id
                )
                chat_group_members = [ChatGroupMembers(user_id=request.user.id, group_id=chat_group.id)]
                for user_id in users:
                    chat_group_members.append(ChatGroupMembers(user_id=user_id, group_id=chat_group.id))

                ChatGroupMembers.objects.bulk_create(chat_group_members, batch_size=50)
            else:
                chat_room = ChatRoom.objects.get(content_type=content_type, object_id=chat_group.id)
            chat_group_members = chat_group.chatgroupmembers_set.values(
                "user__id", "user__username", "user__first_name", "user__last_name"
                ).annotate(
                    user_id=F("user_id"), username=F("user__username"), full_name=Concat(F("user__first_name"), Value(" "), F("user__last_name"))
                ).values("user_id", "username", "full_name")
            
            data = {"room_id": chat_room.id, "group_id": chat_group.id, "group_name": chat_group.group_name, "group_members": list(chat_group_members)}
        return JsonResponse(data)


class ChatUsersAndGroups(View):

    def get(self, request, *args, **kwargs):
        user_content_type = ContentType.objects.get_for_model(User)
        group_content_type = ContentType.objects.get_for_model(ChatGroup)
        # users = User.objects.all()
        models = {
            "chat_group": ChatGroup,
            "chat_group_members": ChatGroupMembers
        }
        users_data = ChatMesssage.objects.get_chat_message_users(user_content_type, request.user.id)
        groups_data = ChatMesssage.objects.get_chat_message_groups(group_content_type, request.user.id, models)
        data = {"users_data": users_data, "groups_data": groups_data}
        return JsonResponse(data)
        # return render(request, "chat/chat_users_and_groups.html", context={"users": users})


class ChatMessagesView(View):

    def post(self, request, *args, **kwargs):
        sender = request.user.id
        data = json.loads(request.body)
        chat_message = ChatMesssage.objects.create_chat_message(sender, data)
        return JsonResponse({"message": chat_message.message, "sender": sender, "room_id": chat_message.chat_room.id})
    
    def get(self, request, *args, **kwargs):
        page_size = 10
        room_id = request.GET.get('room_id')
        start = int(request.GET.get("start", 0))
        end = start + page_size
        chat_messages = ChatMesssage.objects.get_specific_room_chat(room_id, request.user.id, start, end)

        if start == 0:
            chat_messages = list(reversed(chat_messages))
        else:
            # when we scroll up at that time we dont require reverse chat messages
            chat_messages = list(chat_messages)
        data = {"chat_messages": chat_messages, "end": end}

        return JsonResponse(data)
