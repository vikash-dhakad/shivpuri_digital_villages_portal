"""Grievance and Feedback serializers."""

from rest_framework import serializers
from grievances.models import Grievance, Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.name', read_only=True)
    userRole = serializers.CharField(source='user.role', read_only=True)
    grievanceTitle = serializers.CharField(source='grievance.title', read_only=True)
    grievanceCategory = serializers.CharField(source='grievance.category', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    workQualityDisplay = serializers.CharField(source='get_work_quality_display', read_only=True)
    grievanceId = serializers.IntegerField(source='grievance_id', read_only=True)

    class Meta:
        model = Feedback
        fields = [
            'id', 'grievanceId', 'grievanceTitle', 'grievanceCategory',
            'problem_title', 'work_quality', 'workQualityDisplay',
            'rating', 'comments', 'userName', 'userRole', 'createdAt',
        ]
        read_only_fields = ['user', 'village', 'createdAt']

    def validate_comments(self, value):
        if value:
            word_count = len(value.strip().split())
            if word_count > 50:
                raise serializers.ValidationError(
                    f"Feedback maximum 50 shabdon (words) ka hona chahiye. (Aapke words: {word_count})"
                )
        return value


class GrievanceSerializer(serializers.ModelSerializer):
    photoUrl = serializers.CharField(source='photo_url', allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    userId = serializers.IntegerField(source='user_id', read_only=True)
    userName = serializers.CharField(source='user.name', read_only=True)
    userPhone = serializers.CharField(source='user.phone', read_only=True)
    villageId = serializers.IntegerField(source='village_id', read_only=True)
    villageName = serializers.CharField(source='village.name', read_only=True)
    hasFeedback = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = Grievance
        fields = [
            'id', 'title', 'description', 'category', 'status', 'photoUrl',
            'escalated', 'createdAt', 'updatedAt',
            'userId', 'userName', 'userPhone', 'villageId', 'villageName',
            'hasFeedback', 'feedback',
        ]

    def get_hasFeedback(self, obj):
        return hasattr(obj, 'feedback') and obj.feedback is not None

    def get_feedback(self, obj):
        if hasattr(obj, 'feedback') and obj.feedback is not None:
            return {
                'id': obj.feedback.id,
                'problem_title': obj.feedback.problem_title,
                'work_quality': obj.feedback.work_quality,
                'workQualityDisplay': obj.feedback.get_work_quality_display(),
                'rating': obj.feedback.rating,
                'comments': obj.feedback.comments,
            }
        return None
