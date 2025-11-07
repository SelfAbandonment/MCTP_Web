from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "nickname", "qq", "is_staff", "is_whitelisted", "is_active", "created_at")
    search_fields = ("username", "nickname", "qq")
    list_filter = ("is_whitelisted", "is_staff", "is_active")
    readonly_fields = ("last_login", "date_joined", "views")

