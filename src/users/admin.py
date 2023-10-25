from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username', 'last_login')}),
        ('Permissions', {'fields': (
            'is_active', 
            'is_staff', 
            'is_superuser',
            'groups', 
            'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'username', 'first_name', 'last_name', 'contact_number', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'username', 'first_name', 'last_name', 'contact_number', 'is_staff', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username')
    ordering = ('email', 'username')
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)
