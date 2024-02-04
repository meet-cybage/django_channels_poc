import json
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from users.models import User
from chat.models import ChatGroup, ChatRoom

# Create your views here.


class ChatView(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, "chat/chat.html")
        # return HttpResponse("Successfully Logged In!!!!!", content_type="text/plain")


class ChatRoomView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        
        if data.get("room_type") == "user":
            user_id = data.get("users")
            content_type = ContentType.objects.get_for_model(User)

            chat_room = ChatRoom.objects.get_user_room(content_type, request.user.id, user_id).first()

            if not chat_room:
                chat_room = ChatRoom.objects.create(
                    content_type=content_type,
                    object_id=request.user.id,
                    room_associated_member_id=user_id
                )
                
            return JsonResponse({
                "room_id": chat_room.id, 
                "user": chat_room.room_associated_member.id,
                "full_name": f"{chat_room.room_associated_member.first_name} {chat_room.room_associated_member.last_name}",
                "username": chat_room.room_associated_member.username
                })
        else:
            content_type = ContentType.objects.get_for_model(ChatGroup)
        return
