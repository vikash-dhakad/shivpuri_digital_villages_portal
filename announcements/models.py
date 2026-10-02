"""Announcement model — matches existing Announcement.java exactly."""

from django.db import models
from accounts.models import User, Village


class AnnouncementPriority(models.TextChoices):
    NORMAL = 'NORMAL', 'Normal'
    IMPORTANT = 'IMPORTANT', 'Important'
    URGENT = 'URGENT', 'Urgent'


class Announcement(models.Model):
    """Announcement entity — matches existing Announcement.java exactly."""
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='announcements'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='announcements'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(
        max_length=20, choices=AnnouncementPriority.choices,
        default=AnnouncementPriority.NORMAL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
