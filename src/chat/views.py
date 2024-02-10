import json
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from users.models import User
from chat.models import ChatGroup, ChatGroupMembers, ChatRoom

# Create your views here.


class ChatView(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, "chat/chat.html")
        # return HttpResponse("Successfully Logged In!!!!!", content_type="text/plain")


class ChatRoomView(View):

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
                group_members = chat_group.chatgroupmembers_set.values("user__id", "user__username", "user__first_name")
            else:
                chat_room = ChatRoom.objects.get(chat_room=chat_group)
                chat_group_members = chat_group.chatgroupmembers_set.all()

        return
