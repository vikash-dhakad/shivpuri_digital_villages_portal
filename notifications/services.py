"""Notification service — matches NotificationService.java exactly.
Creates and persists notifications, then pushes via WebSocket.
"""

import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from notifications.models import Notification, NotificationType
from accounts.models import User

logger = logging.getLogger(__name__)


def send_notification(user_id, title, message, notification_type, reference_id=None):
    """Create and persist a notification, then push it via WebSocket.
    Matches NotificationService.sendNotification() exactly.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
        reference_id=reference_id,
    )

    # Push real-time via WebSocket
    response = {
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'type': notification.type,
        'read': notification.is_read,
        'referenceId': notification.reference_id,
        'createdAt': notification.created_at.isoformat() if notification.created_at else None,
    }

    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',
            {
                'type': 'send_notification',
                'data': response,
            }
        )
    except Exception as e:
        logger.warning(f'WebSocket push failed for user {user_id}: {e}')


def send_to_village(village_id, title, message, notification_type, reference_id=None):
    """Send notification to all users in a village.
    Matches NotificationService.sendToVillage() exactly.
    """
    village_users = User.objects.filter(village_id=village_id)
    for user in village_users:
        send_notification(user.id, title, message, notification_type, reference_id)
