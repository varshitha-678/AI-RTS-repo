from django.contrib import admin
from ats_app.models import UserProfile, UploadedResume

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "mongo_user_id"]

@admin.register(UploadedResume)
class UploadedResumeAdmin(admin.ModelAdmin):
    list_display = ["user", "filename", "uploaded_at"]
