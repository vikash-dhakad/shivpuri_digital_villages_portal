from django.contrib import admin
from grievances.models import Grievance, Feedback

@admin.register(Grievance)
class GrievanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'status', 'escalated', 'user', 'village', 'created_at']
    list_filter = ['status', 'category', 'escalated', 'village']
    search_fields = ['title', 'description']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'problem_title', 'work_quality', 'rating', 'user', 'village', 'created_at']
    list_filter = ['work_quality', 'rating', 'village']
    search_fields = ['problem_title', 'comments']
