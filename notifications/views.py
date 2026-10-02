"""Notification views — matches NotificationController.java exactly."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_notifications(request):
    """GET /api/notifications/ — get all notifications for current user."""
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """GET /api/notifications/unread-count/ — get unread notification count."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'count': count})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, pk):
    """PUT /api/notifications/<id>/read/ — mark single notification as read."""
    try:
        notification = Notification.objects.get(id=pk)
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    """PUT /api/notifications/read-all/ — mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    """DELETE /api/notifications/<id>/ — delete single notification."""
    Notification.objects.filter(id=pk).delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all(request):
    """DELETE /api/notifications/clear/ — delete all notifications for user."""
    Notification.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_200_OK)
