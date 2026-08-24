from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "get_full_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone",)}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = "Full name"
