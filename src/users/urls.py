

from django.urls import path
from users.views import UsersView


urlpatterns = [
    path("get/users", UsersView.as_view(), name="get_users")
]
