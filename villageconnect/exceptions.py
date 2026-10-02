"""Custom exception handler for VillageConnect REST API."""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Handle exceptions and return consistent error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Handle unhandled exceptions
    if isinstance(exc, ValueError):
        return Response(
            {'error': str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )

    return Response(
        {'error': str(exc)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
