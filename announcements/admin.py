from django.contrib import admin
from announcements.models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'priority', 'village', 'created_by', 'created_at']
    list_filter = ['priority', 'village']
    search_fields = ['title', 'message']
