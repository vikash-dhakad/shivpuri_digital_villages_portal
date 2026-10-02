"""Announcement views — matches AnnouncementController.java + AnnouncementService.java exactly."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from announcements.models import Announcement, AnnouncementPriority
from announcements.serializers import AnnouncementSerializer
from accounts.permissions import IsPanchayatAdmin
from notifications.models import NotificationType
from notifications.services import send_to_village


@api_view(['POST'])
@permission_classes([IsPanchayatAdmin])
def create_announcement(request):
    """POST /api/announcements/ — create announcement (PANCHAYAT_ADMIN only).
    Matches AnnouncementService.createAnnouncement() exactly.
    """
    user = request.user
    village = user.village
    if village is None:
        return Response(
            {'error': 'User must be associated with a village'},
            status=status.HTTP_400_BAD_REQUEST
        )

    title = request.data.get('title', '')
    message = request.data.get('message', '')
    priority = request.data.get('priority', 'NORMAL')

    announcement = Announcement.objects.create(
        village=village,
        created_by=user,
        title=title,
        message=message,
        priority=priority,
    )

    serializer = AnnouncementSerializer(announcement)

    # Send persistent notification to all village users
    send_to_village(
        village.id,
        f'\U0001f4e2 {title}',
        message,
        NotificationType.ANNOUNCEMENT,
        announcement.id,
    )

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def village_announcements(request, village_id):
    """GET /api/announcements/village/<id>/ — get village announcements."""
    announcements = Announcement.objects.filter(village_id=village_id)
    serializer = AnnouncementSerializer(announcements, many=True)
    return Response(serializer.data)
