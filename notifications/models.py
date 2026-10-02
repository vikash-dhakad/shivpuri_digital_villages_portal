"""Notification model — matches existing Notification.java exactly."""

from django.db import models
from accounts.models import User


class NotificationType(models.TextChoices):
    GRIEVANCE = 'GRIEVANCE', 'Grievance'
    BOOKING = 'BOOKING', 'Booking'
    SOS = 'SOS', 'SOS'
    ANNOUNCEMENT = 'ANNOUNCEMENT', 'Announcement'
    EQUIPMENT = 'EQUIPMENT', 'Equipment'
    FINANCE = 'FINANCE', 'Finance'
    SYSTEM = 'SYSTEM', 'System'


class Notification(models.Model):
    """Notification entity — matches existing Notification.java exactly."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    is_read = models.BooleanField(default=False)
    reference_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.user.name}"
