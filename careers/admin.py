from django.contrib import admin

from .models import ContactMessage, Profile, QuizResult


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__email", "user__first_name")


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "variety_preference", "created_at")
    list_filter = ("variety_preference", "created_at")
    readonly_fields = ("answers", "top_matches", "category_scores", "created_at")
    search_fields = ("user__email",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "resolved")
    list_filter = ("resolved", "created_at")
    list_editable = ("resolved",)
    search_fields = ("name", "email", "message")
