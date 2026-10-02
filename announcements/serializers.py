"""Announcement serializers matching AnnouncementResponse.java."""

from rest_framework import serializers
from announcements.models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    createdByName = serializers.CharField(source='created_by.name', read_only=True)
    createdByRole = serializers.CharField(source='created_by.role', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    villageId = serializers.IntegerField(source='village_id', read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'priority', 'createdByName', 'createdByRole', 'createdAt', 'villageId']
