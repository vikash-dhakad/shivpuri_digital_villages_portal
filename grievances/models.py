"""Grievance model — matches existing Grievance.java exactly."""

from django.db import models
from accounts.models import User, Village


class GrievanceCategory(models.TextChoices):
    INFRASTRUCTURE = 'INFRASTRUCTURE', 'Infrastructure'
    WATER = 'WATER', 'Water'
    ELECTRICITY = 'ELECTRICITY', 'Electricity'
    AGRICULTURE = 'AGRICULTURE', 'Agriculture'
    OTHERS = 'OTHERS', 'Others'


class GrievanceStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    RESOLVED = 'RESOLVED', 'Resolved'
    REOPENED = 'REOPENED', 'Reopened'


from django.core.exceptions import ValidationError


def validate_max_50_words(value):
    if value:
        word_count = len(value.strip().split())
        if word_count > 50:
            raise ValidationError(f"Feedback 50 shabdon (words) se zyada nahi ho sakta. (Current words: {word_count})")


class Grievance(models.Model):
    """Grievance entity — matches existing Grievance.java exactly."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=GrievanceCategory.choices)
    status = models.CharField(
        max_length=20, choices=GrievanceStatus.choices,
        default=GrievanceStatus.PENDING
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='grievances'
    )
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='grievances'
    )
    photo_url = models.CharField(max_length=500, blank=True, null=True)
    escalated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'grievances'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"


class Feedback(models.Model):
    """Citizen feedback submitted by Villagers/Farmers after a grievance is resolved."""
    WORK_QUALITY_CHOICES = [
        ('BAHUT_ACHHA', 'Bahut Badhiya (Excellent)'),
        ('ACHHA', 'Achha Kaam Hua (Good)'),
        ('THEEK', 'Theek-thaak (Satisfactory)'),
        ('ASANTUSHT', 'Asantusht (Unsatisfactory)'),
    ]

    grievance = models.OneToOneField(
        Grievance, on_delete=models.CASCADE, related_name='feedback'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feedbacks'
    )
    village = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name='feedbacks'
    )
    problem_title = models.CharField(
        max_length=255,
        verbose_name="Problem kya thi"
    )
    work_quality = models.CharField(
        max_length=50,
        choices=WORK_QUALITY_CHOICES,
        default='ACHHA',
        verbose_name="Kaisa kaam hua"
    )
    rating = models.IntegerField(default=5)  # 1 to 5 stars
    comments = models.TextField(
        validators=[validate_max_50_words],
        verbose_name="Feedback (Max 50 Words)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'grievance_feedbacks'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback on '{self.problem_title}' by {self.user.name}"
