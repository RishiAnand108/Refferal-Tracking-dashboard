# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model        = CustomUser
    list_display = ['username', 'email', 'phone', 'city', 'role', 'is_staff']
    fieldsets    = UserAdmin.fieldsets + (
        ('Concave Insights Info', {
            'fields': ('phone', 'city', 'role')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Concave Insights Info', {
            'fields': ('phone', 'city', 'role')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)