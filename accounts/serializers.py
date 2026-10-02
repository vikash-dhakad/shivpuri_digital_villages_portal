"""Serializers for accounts app — Auth DTOs matching Spring Boot exactly."""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User, Village, UserRole


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = ['id', 'name', 'block', 'district', 'state', 'pincode', 'latitude', 'longitude']


class RegisterSerializer(serializers.Serializer):
    """Matches RegisterRequest.java exactly."""
    name = serializers.CharField(max_length=150)
    phone = serializers.RegexField(regex=r'^\d{10}$', error_messages={
        'invalid': 'Phone number must be 10 digits'
    })
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserRole.choices)
    # For VILLAGER/FARMER — select existing village
    villageId = serializers.IntegerField(required=False, allow_null=True)
    # For PANCHAYAT_ADMIN — create new village
    villageName = serializers.CharField(required=False, allow_blank=True)
    district = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    block = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.CharField(required=False, allow_blank=True)


class LoginSerializer(serializers.Serializer):
    """Matches LoginRequest.java exactly."""
    phone = serializers.CharField()
    password = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    """Matches AuthResponse.java exactly."""
    token = serializers.CharField()
    refreshToken = serializers.CharField()
    userId = serializers.IntegerField()
    name = serializers.CharField()
    phone = serializers.CharField(required=False)
    role = serializers.CharField()
    villageId = serializers.IntegerField(allow_null=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that includes role claim — matches JwtUtil.java."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = f'ROLE_{user.role}'
        token['phone'] = user.phone
        return token


class UserSerializer(serializers.ModelSerializer):
    village = VillageSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email', 'role', 'village', 'is_active', 'created_at']
