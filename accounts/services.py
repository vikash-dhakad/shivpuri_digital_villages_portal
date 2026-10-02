"""SMS utility service using Fast2SMS for OTP & alerts."""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

FAST2SMS_URL = 'https://www.fast2sms.com/dev/bulkV2'


def send_sms(phone_numbers, message, otp=None):
    """Send SMS via Fast2SMS API.
    Supports dedicated Fast2SMS 'otp' route (no DLT required) and 'q' route for alerts.
    """
    api_key = getattr(settings, 'FAST2SMS_API_KEY', '')
    if not api_key or not api_key.strip():
        logger.warning(f'Fast2SMS API Key is missing. SMS not sent. Message was: {message}')
        return None

    try:
        numbers = ','.join(phone_numbers) if isinstance(phone_numbers, list) else str(phone_numbers)
        headers = {
            'authorization': api_key.strip(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        if otp:
            data = {
                'variables_values': str(otp),
                'route': 'otp',
                'numbers': numbers,
            }
        else:
            data = {
                'route': 'q',
                'message': message,
                'language': 'english',
                'flash': '0',
                'numbers': numbers,
            }
        response = requests.post(FAST2SMS_URL, headers=headers, data=data, timeout=10)
        logger.info(f'SMS Sent via Fast2SMS to {numbers}. Response: {response.text}')
        return response.json()
    except Exception as e:
        logger.error(f'Failed to send SMS via Fast2SMS: {e}')
        return None
