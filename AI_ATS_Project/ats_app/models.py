"""
Django models — minimal, since primary storage is MongoDB.
We keep Django's built-in User model and add a Profile.
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("user", "User"),
        ("guest", "Guest"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user")
    mongo_user_id = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class UploadedResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    filename = models.CharField(max_length=255)
    mongo_resume_id = models.CharField(max_length=64, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
