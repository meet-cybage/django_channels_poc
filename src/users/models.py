from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator
from users.managers.user_manager import UserManager

# Create your models here.



class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    contact_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True) # Validators should be a list

    objects = UserManager()
    
    def __str__(self) -> str:
        return self.username
