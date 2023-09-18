from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'phone_number', 'email', 'is_active', 'is_staff', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'phone_number']
    ordering = ['username']

    fieldsets = [
        ('Info', {'fields': ['username', 'password']}),
        ('Personal info', {'fields': ['first_name', 'last_name', 'email']}),
        ('Permissions', {'fields': ['is_active', 'is_staff', 'is_superuser']}),
        ('Additional information', {'fields': ['phone_number', 'biography', 'job', 'date_of_birth', 'photo']}),
    ]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'description', 'created']
    list_filter = ['created']
    search_fields = ['description']
    raw_id_fields = ['author']
    ordering = ['created']
