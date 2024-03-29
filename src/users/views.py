from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.db.models import Q, F, Value, CharField
from django.db.models.functions import Concat
from allauth.account.views import LoginView, SignupView
from users.models import User
# Create your views here.

class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data here
        return context

    def form_valid(self, form):
        # This method is called when the form is successfully submitted
        response = super().form_valid(form)
        # You can add additional logic here if needed
        return response

    def form_invalid(self, form):
        # This method is called when the form submission is invalid
        response = super().form_invalid(form)
        # You can add additional logic here if needed
        return response


class CustomSignUpView(SignupView):
    template_name = "users/signup.html"


class UsersView(View):

    def get(self, request):
        users = User.objects.filter(
            ~Q(id=request.user.id), ~Q(is_superuser=True)
        ).annotate(full_name=Concat(F("first_name"), Value(" "), F("last_name"), output_field=CharField())).values("id", "username", "full_name")
        return JsonResponse(list(users), safe=False)
