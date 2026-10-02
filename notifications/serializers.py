"""Notification serializers matching NotificationResponse.java."""

from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    read = serializers.BooleanField(source='is_read')
    referenceId = serializers.IntegerField(source='reference_id', allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'read', 'referenceId', 'createdAt']
