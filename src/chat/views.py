from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

# Create your views here.


class ChatView(View):
    
    def get(self, request, *args, **kwargs):
        return render(request, "chat/chat.html")
        # return HttpResponse("Successfully Logged In!!!!!", content_type="text/plain")
