"""Auth views — Register, Login, Refresh Token, Logout.
Matches AuthController.java + AuthService.java logic exactly.
"""

import logging
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Village
from accounts.serializers import RegisterSerializer, LoginSerializer

logger = logging.getLogger(__name__)


def _build_auth_response(user, refresh):
    """Build auth response matching AuthResponse.java."""
    return {
        'token': str(refresh.access_token),
        'refreshToken': str(refresh),
        'userId': user.id,
        'name': user.name,
        'phone': user.phone,
        'role': user.role,
        'villageId': user.village_id,
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """POST /api/auth/register — matches AuthService.register() exactly."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Check if phone already registered
    if User.objects.filter(phone=data['phone']).exists():
        return Response(
            {'error': 'Phone number is already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )

    village = None

    if data.get('villageId'):
        # Flow 1: VILLAGER/FARMER selects an existing village from dropdown
        try:
            village = Village.objects.get(id=data['villageId'])
        except Village.DoesNotExist:
            return Response(
                {'error': 'Village not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif data.get('villageName') and data['villageName'].strip():
        # Flow 2: PANCHAYAT_ADMIN registers a village (reuse if already exists with same name & district)
        v_name = data['villageName'].strip()
        v_dist = data.get('district', '').strip()
        village = Village.objects.filter(name__iexact=v_name, district__iexact=v_dist).first()
        if not village:
            village = Village.objects.create(
                name=v_name,
                district=v_dist,
                state=data.get('state', '').strip(),
                block=data.get('block', '').strip(),
                pincode=data.get('pincode', '').strip(),
            )

    user = User.objects.create_user(
        phone=data['phone'],
        password=data['password'],
        name=data['name'],
        email=data.get('email') or None,
        role=data['role'],
        village=village,
    )

    refresh = RefreshToken.for_user(user)
    return Response(_build_auth_response(user, refresh))


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """POST /api/auth/login — authenticates user and returns JWT tokens."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = authenticate(request, username=data['phone'], password=data['password'])
    if user is None:
        return Response(
            {'error': 'Invalid phone number or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response(_build_auth_response(user, refresh))


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """POST /api/auth/refresh-token — validates refresh token and returns new access/refresh tokens."""
    refresh_token_str = request.data.get('refreshToken')
    if not refresh_token_str:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        old_refresh = RefreshToken(refresh_token_str)
        user_id = old_refresh.payload.get('user_id')
        user = User.objects.get(id=user_id)

        # Generate new tokens (rolling refresh token)
        new_refresh = RefreshToken.for_user(user)
        return Response(_build_auth_response(user, new_refresh))
    except Exception as e:
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """POST /api/auth/logout — logs out user."""
    return Response('Logged out successfully')


# ─── Forgot Password (OTP Verification & Reset) ──────────────────────

import random
from django.conf import settings
from accounts.services import send_sms


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_send_otp(request):
    """POST /api/auth/forgot-password/send-otp/ — sends a 6-digit OTP for password reset."""
    phone = request.data.get('phone', '').strip()
    if not phone or len(phone) < 10:
        return Response({'error': 'Kripya ek valid 10-digit phone number dalein.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user exists
    user = User.objects.filter(phone=phone).first()
    if not user:
        return Response({'error': 'Is phone number ke saath koi account registered nahi hai.'}, status=status.HTTP_404_NOT_FOUND)

    # Generate 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    cache.set(f'PWD_RESET_OTP:{phone}', otp, timeout=600)  # 10 minutes

    # Send SMS if Fast2SMS configured
    sms_text = f"Your VillageConnect password reset OTP is {otp}. Valid for 10 minutes. Do not share it with anyone."
    try:
        send_sms([phone], sms_text, otp=otp)
    except Exception as e:
        logger.warning(f"SMS sending error: {e}")

    logger.info(f"PASSWORD RESET OTP for {phone}: {otp}")

    response_payload = {
        'message': f"OTP aapke phone number (+91 {phone}) par bhej diya gaya hai.",
        'phone': phone,
    }
    if settings.DEBUG:
        response_payload['devOtp'] = otp

    return Response(response_payload, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_verify_and_reset(request):
    """POST /api/auth/forgot-password/verify-and-reset/ — verifies OTP and sets new password."""
    phone = request.data.get('phone', '').strip()
    otp = request.data.get('otp', '').strip()
    new_password = request.data.get('newPassword', '').strip()

    if not phone or not otp or not new_password:
        return Response({'error': 'Phone number, OTP aur naya Password sabhi required hain.'}, status=status.HTTP_400_BAD_REQUEST)

    if len(new_password) < 4:
        return Response({'error': 'Password kam se kam 4 characters ka hona chahiye.'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify cached OTP
    cached_otp = cache.get(f'PWD_RESET_OTP:{phone}')
    if not cached_otp or str(cached_otp).strip() != str(otp).strip():
        return Response({'error': 'Galat ya expired OTP! Kripya sahi OTP dalein ya resend karein.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(phone=phone).first()
    if not user:
        return Response({'error': 'User account nahi mila.'}, status=status.HTTP_404_NOT_FOUND)

    # Update password
    user.set_password(new_password)
    user.save(update_fields=['password'])

    # Invalidate OTP
    cache.delete(f'PWD_RESET_OTP:{phone}')

    logger.info(f"Password successfully reset for user phone: {phone}")

    return Response({
        'message': 'Password successfully reset ho gaya hai! Ab aap naye password se login kar sakte hain.'
    }, status=status.HTTP_200_OK)


# View aliases for standard navigation and import conventions
login_view = login
register_view = register


