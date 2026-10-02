"""WebSocket consumer for real-time notifications.
Matches Spring Boot STOMP WebSocket /topic/notifications/* pattern.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """Handles WebSocket connections for real-time notifications."""

    async def connect(self):
        self.user = self.scope.get('user')
        if self.user and self.user.is_authenticated:
            # Add to user-specific group
            self.user_group = f'notifications_{self.user.id}'
            await self.channel_layer.group_add(self.user_group, self.channel_name)

            # Add to village group if user has a village
            if self.user.village_id:
                self.village_group = f'village_{self.user.village_id}'
                await self.channel_layer.group_add(self.village_group, self.channel_name)

            await self.accept()
            logger.info(f'WebSocket connected: user {self.user.phone}')
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if hasattr(self, 'village_group'):
            await self.channel_layer.group_discard(self.village_group, self.channel_name)
        logger.info(f'WebSocket disconnected: code {close_code}')

    async def receive(self, text_data):
        """Handle incoming messages from clients (if needed)."""
        pass

    async def send_notification(self, event):
        """Send notification data to WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))

    async def village_broadcast(self, event):
        """Send village-wide broadcast to WebSocket client."""
        await self.send(text_data=json.dumps(event['data']))
