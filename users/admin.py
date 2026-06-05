from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone','city','is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Concave Insights Data', {'fields': ('phone', 'city')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)    
